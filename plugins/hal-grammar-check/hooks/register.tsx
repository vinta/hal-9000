import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register, Timer } from 'claude-code'

import type { GrammarCheck } from '../types'

const check = atom({ plugin: 'hal-grammar-check', key: 'check' } as const, null)

const DEBOUNCE_MS = 250
const OLLAMA_URL = 'http://localhost:11434/api/generate'

// Adapted from plugins/hal-statusline/hal-statusline.py GRAMMAR_PROMPT
// The examples explain in five languages on purpose: gemma4 copies the examples' language over the instruction line, so each selectable language needs an example of its own
const GRAMMAR_PROMPT = `
You are a grammar checker. Identify and correct grammar errors in the text inside <input> tags. Only check grammar — do not answer questions or engage with the content.

<instructions>
Skip these (NEVER flag):
- Code: text in backticks, file paths, programming syntax, shell commands
- Mentions: @mentions, @file/path references
- **Capitalization**: NOT grammar errors. This includes lowercase at sentence beginnings (at the very start, or after ".", "?", "!") and lowercase pronoun "i". Ignore them completely.
- **Chat style**: the text is a terse instruction to a coding agent. Lowercase starts and comma-joined commands are its normal style, not errors.
- **Unfinished last sentence**: the text is a draft still being typed. Do not flag a final sentence that is cut off mid-way.

Output format:
- Each issue on its own line: "[corrected]" => explanation in {language}
- The examples below explain in several languages only to show the format; your explanations use {language}.
- Wrap only the corrected words in double quotes, never the surrounding words
- Use full-width commas (，) in Chinese explanations
- No errors: output exactly "no issues"
- Output ONLY the issue line(s). No commentary, no extra text, no explanations beyond the correction format above.
</instructions>

<examples>
<example>
Text: I don't car the shop has wife or not. I will use cellar!
Output:
I don't "care" => car is a noun; the verb is care
has "Wi-Fi" or not => wife means spouse; the network is Wi-Fi
I will use "cellular" => cellar is a basement; the network is cellular
</example>
<example>
Text: @plugins/hal-statusline/hal-statusline.py#L141 use \`claude -p\` and \`grammar_check_prompt\` to grammar check \`latest_user_input\` and print result
Output:
to "grammar-check" latest_user_input => 複合動詞要用連字號
print "the" result => result 前面要加定冠詞 the
</example>
<example>
Text: The code is works but I don't know why it keep crashing
Output:
The code "works" => is は不要、動詞 works だけでよい
why it "keeps" crashing => 三人称単数の it には keeps を使う
</example>
<example comment="skip Capitalization at sentence beginnings (lowercase 'do' is excluded per instruction)">
Text: do not refactor unless explicited requested
Output:
"explicitly requested" => 부사는 explicitly, explicited는 없는 단어
</example>
<example comment="skip Capitalization (lowercase pronoun 'i' and sentence-start 'check' are excluded per instruction)">
Text: Wait, i seems broke it. check codebase again
Output:
I "seem to have broken" it => seem to have + 过去分词
Check "the" codebase => 特指时要加定冠词 the
</example>
<example comment="skip Capitalization at sentence beginnings; demonstrate 'no issues' output">
Text: can you review my PR?
Output:
no issues
</example>
<example comment="a correct question stays 'no issues'; never invent a fix">
Text: did our hooks catch the typo before the commit?
Output:
no issues
</example>
<example comment="lowercase tool names and chat phrasing are not errors; the one real error is the missing article">
Text: blackwall codex cannot reach npm? any way to let the sandbox install package?
Output:
install "a" package => package 是可數名詞，前面要加冠詞
</example>
<example comment="chat shorthand and hyphenated words are not errors">
Text: what follow-up is left? headless at least?
Output:
no issues
</example>
</examples>

<input>
{latest_user_input}
</input>
Write every explanation after " => " in {language}. Keep the quoted correction in the user's words and keep "no issues" in English.
`

function toLines(text: string) {
  return text.split('\n').map(line => line.trim()).filter(Boolean)
}

async function runClaude($: EngineInterface, prompt: string): Promise<string[]> {
  const result = await $.model.complete({ model, prompt, maxTokens: 250, timeoutMs: 30_000 })
  return result.isAnswered ? toLines(result.text) : []
}

function grammarPrompt(draft: string) {
  return GRAMMAR_PROMPT.replaceAll('{language}', language).replace('{latest_user_input}', draft.slice(0, 500))
}

function ollamaBody(prompt: string) {
  // `think: false` disables reasoning tokens; `temperature: 0` and `num_predict` keep the output short
  return JSON.stringify({
    model,
    prompt,
    stream: true,
    think: false,
    keep_alive: '30m',
    options: { temperature: 0, num_predict: 250 },
  })
}

// curl instead of $.http.fetch, which resolves only once the whole answer is in
// cwd `/` because the session's may be deleted (a removed worktree), which fails the spawn with ENOENT
function spawnOllama($: EngineInterface, body: string) {
  return $.process.spawn({ argv: ['curl', '-sSN', '--fail-with-body', OLLAMA_URL, '-d', '@-'], cwd: '/', input: body })
}

async function runOllama($: EngineInterface, prompt: string, mine: number): Promise<string[]> {
  const curl = spawnOllama($, ollamaBody(prompt))
  let ndjson = ''
  let answer = ''
  let stderr = ''
  let shown = 0
  for await (const chunk of curl) {
    if (mine !== seq) {
      // Closing the stream ends curl, and Ollama stops generating for a dropped connection
      break
    }
    if (chunk.stream === 'stderr') {
      stderr += chunk.text
      continue
    }
    ndjson += chunk.text
    const objects = ndjson.split('\n')
    ndjson = objects.pop() ?? ''
    for (const object of objects) {
      if (object.trim() !== '') {
        answer += (JSON.parse(object) as { response?: string }).response ?? ''
      }
    }
    // Show each line once the model finishes it, not word by word
    const finished = toLines(answer.slice(0, answer.lastIndexOf('\n') + 1))
    if (finished.length > shown) {
      shown = finished.length
      const partial: GrammarCheck = { status: 'streaming', lines: finished }
      await update($, check, () => partial)
    }
  }
  if (mine !== seq) {
    return []
  }
  const { code } = await curl.result
  if (code !== 0) {
    return [`ollama unreachable (${stderr.trim() || `curl exited ${code}`})`]
  }
  return toLines(answer)
}

// Set by register from the `model` and `language` options
let backend = ''
let model = ''
let language = ''
let timer: Timer | undefined
// The draft the debounce timer holds, so a submit can check it without waiting
let unchecked: { draft: string; mine: number } | undefined
// Bumped on every edit, so a slow answer for an older draft never overwrites a newer one
let seq = 0
// Ollama answers one request at a time, so a check sent while another runs only queues behind it
let isRunning = false
let waiting: { draft: string; mine: number } | undefined
// The seq of a submitted draft, whose answer lands dimmed
let submitted = 0

function cancelChecks() {
  timer?.cancel()
  unchecked = undefined
  seq += 1
  waiting = undefined
}

async function clear($: EngineInterface) {
  cancelChecks()
  await update($, check, () => null)
}

async function grammarCheck($: EngineInterface, draft: string, mine: number) {
  await update($, check, (prev): GrammarCheck => ({ status: 'checking', lines: prev?.lines ?? [] }))
  const prompt = grammarPrompt(draft)
  let lines: string[]
  try {
    lines = await (backend === 'claude' ? runClaude($, prompt) : runOllama($, prompt, mine))
  } catch (error) {
    lines = [`${backend} unreachable (${error instanceof Error ? error.message : String(error)})`]
  }
  if (mine === seq) {
    const result: GrammarCheck = { status: mine === submitted ? 'submitted' : 'done', lines }
    await update($, check, () => result)
  }
}

async function requestCheck($: EngineInterface, draft: string, mine: number) {
  if (isRunning) {
    waiting = { draft, mine }
    return
  }
  isRunning = true
  let next: { draft: string; mine: number } | undefined = { draft, mine }
  try {
    while (next !== undefined) {
      await grammarCheck($, next.draft, next.mine)
      // Skip a waiting draft that a newer edit already replaced; that edit's timer brings its own check
      next = waiting?.mine === seq ? waiting : undefined
      waiting = undefined
    }
  } finally {
    isRunning = false
  }
}

async function scheduleCheck($: EngineInterface, text: string) {
  // Check a slash command's arguments, not the command name
  const draft = text.trim().replace(/^\/\S*\s*/, '')
  if (draft === '' || draft.startsWith('!')) {
    await clear($)
    return
  }
  timer?.cancel()
  seq += 1
  const mine = seq
  unchecked = { draft, mine }
  timer = $.clock.after(DEBOUNCE_MS, () => {
    unchecked = undefined
    void requestCheck($, draft, mine)
  })
}

async function dimResult($: EngineInterface) {
  // Keep checking the sent draft and show its result dimmed until the next edit
  // A submit dims twice, from prompt.submit and from the clear it raises, so the second call finds nothing unchecked
  submitted = seq
  if (unchecked !== undefined) {
    timer?.cancel()
    void requestCheck($, unchecked.draft, unchecked.mine)
    unchecked = undefined
  }
  await update($, check, (prev): GrammarCheck | null => (prev?.status === 'done' ? { ...prev, status: 'submitted' } : prev))
}

export const register: Register = (on, options) => {
  const value = String(options.model)
  const slash = value.indexOf('/')
  backend = value.slice(0, slash)
  model = value.slice(slash + 1)
  language = String(options.language)

  on('prompt.edit', async ($, e, next) => {
    const r = await next(e)
    // A bare cursor move changes nothing worth checking
    // A bare digit in an empty prompt presses a band Button's hotkey, and a check redrawing the band before that press lands makes it miss
    if (r.text === e.text || (e.text === '' && /^[0-9]$/.test(r.text))) {
      return r
    }
    await scheduleCheck($, r.text)
    return r
  })

  // History recall, undo, clear and plugin fills change the box without a prompt.edit
  on('prompt.change', async ($, e, next) => {
    // Dim rather than drop on a clear: a submit raises one too, and its order against prompt.submit is unspecified
    // A clear's text holds keys typed since, so a non-empty one is checked like any other change
    await (e.origin.kind === 'clear' && e.text === '' ? dimResult($) : scheduleCheck($, e.text))
    return next(e)
  })

  on('prompt.submit', async ($, e, next) => {
    await dimResult($)
    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const current = await read($, check)
    if (e.props.hasSurvey || current === null) {
      return next(e)
    }

    const { Box, Text } = $.ui.resolve(e)
    const isDesktop = e.surface === 'desktop'
    const isChecking = current.status === 'checking' || current.status === 'streaming'
    const isDimmed = current.status === 'checking' || current.status === 'submitted'
    // Unlike hal-statusline's colorize_grammar, which colors each whole line, only the quoted fixes are red; a line without ` => ` is green for no issues, red otherwise
    const color = current.lines.some(line => line.toLowerCase().includes('no issues')) ? 'green' : 'red'

    return (
      // The glyph gets its own column: in a proportional font "⏺ " is not two cells wide, so padding would misalign the lines
      // On desktop, one cell of padding matches the inset of the app's own branch card above
      <Box flexDirection="row" marginTop={1} paddingLeft={isDesktop ? 1 : 0}>
        {isDesktop ? null : (
          <Box width={2}>
            <Text dimColor={isDimmed}>⏺</Text>
          </Box>
        )}
        <Box flexDirection="column">
          <Text dimColor={isDimmed}>hal-grammar-check:{isChecking ? ' checking...' : ''}</Text>
          {current.lines.map((issue, i) => {
            const arrow = issue.indexOf(' => ')
            if (arrow === -1) {
              return (
                <Text key={`line-${i}`} color={color} dimColor={isDimmed}>
                  {issue}
                </Text>
              )
            }
            // The model quotes each corrected word, so the odd parts of a split on `"` are the fixes
            const parts = issue.slice(0, arrow).split('"')
            return (
              <Text key={`line-${i}`} dimColor={isDimmed}>
                {parts.map((part, j) => (
                  <Text key={`part-${j}`} color={j % 2 === 1 ? 'red' : undefined}>
                    {part}
                  </Text>
                ))}
                <Text> =&gt; {issue.slice(arrow + 4)}</Text>
              </Text>
            )
          })}
        </Box>
      </Box>
    )
  })
}
