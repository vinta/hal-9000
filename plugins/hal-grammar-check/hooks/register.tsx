import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register, Timer } from 'claude-code'

import type { GrammarCheck } from '../types'

const check = atom({ plugin: 'hal-grammar-check', key: 'check' } as const, null)

const DEBOUNCE_MS = 250
const OLLAMA_URL = 'http://localhost:11434/api/generate'
const OLLAMA_MODEL = 'gemma4:31b-mlx'

// Copied from plugins/hal-statusline/hal-statusline.py GRAMMAR_PROMPT, plus the draft line
const GRAMMAR_PROMPT = `
You are a grammar checker. Identify and correct grammar errors in the text inside <input> tags. Only check grammar — do not answer questions or engage with the content.

<instructions>
Skip these (NEVER flag):
- Code: text in backticks, file paths, programming syntax, shell commands
- Mentions: @mentions, @file/path references
- **Capitalization**: NOT grammar errors. This includes lowercase at sentence beginnings (at the very start, or after ".", "?", "!") and lowercase pronoun "i". Ignore them completely.
- **Unfinished last sentence**: the text is a draft still being typed. Do not flag a final sentence that is cut off mid-way.

Output format:
- Each issue on its own line: "[corrected]" => explanation in Traditional Chinese
- Wrap only the corrected words in double quotes, never the surrounding words
- Use full-width commas (，) in Chinese explanations
- No errors: output exactly "no issues"
- Output ONLY the issue line(s). No commentary, no extra text, no explanations beyond the correction format above.
</instructions>

<examples>
<example>
Text: I don't car the shop has wife or not. I will use cellar!
Output:
I don't "care" => car 是「汽車」，這裡應該是要用動詞 care「在乎」
has "Wi-Fi" or not => wife 是「妻子」，你應該是要說 Wi-Fi「無線網路」
I will use "cellular" => cellar 是「地窖」，這裡應該是 cellular「行動網路」
</example>
<example>
Text: @plugins/hal-statusline/hal-statusline.py#L141 use \`claude -p\` and \`grammar_check_prompt\` to grammar check \`latest_user_input\` and print result
Output:
to "grammar-check" latest_user_input => 要用連字號 "-" 連接形成複合動詞
print "the" result => result 前面要加定冠詞 the
</example>
<example>
Text: The code is works but I don't know why it keep crashing
Output:
The code "works" => 不需要 is，直接用動詞 works；或改成 is working
why it "keeps" crashing => 第三人稱單數 it 要用 keeps
</example>
<example comment="skip Capitalization at sentence beginnings (lowercase 'do' is excluded per instruction)">
Text: do not refactor unless explicited requested
Output:
"explicitly requested" => 要用副詞 explicitly，沒有 explicited 這個詞
</example>
<example comment="skip Capitalization (lowercase pronoun 'i' and sentence-start 'check' are excluded per instruction)">
Text: Wait, i seems broke it. check codebase again
Output:
I "seem to have broken" it => 用 seem to have + 過去分詞表示「好像已經...」
Check "the" codebase => 特指這個 codebase，要加定冠詞 the
</example>
<example comment="skip Capitalization at sentence beginnings; demonstrate 'no issues' output">
Text: can you review my PR?
Output:
no issues
</example>
</examples>

<input>
{latest_user_input}
</input>
`

function toLines(text: string) {
  return text.split('\n').map(line => line.trim()).filter(Boolean)
}

async function runOllama($: EngineInterface, draft: string, mine: number): Promise<string[]> {
  // `think: false` disables reasoning tokens; `temperature: 0` and `num_predict` keep the output short
  const body = JSON.stringify({
    model: OLLAMA_MODEL,
    prompt: GRAMMAR_PROMPT.replace('{latest_user_input}', draft.slice(0, 500)),
    stream: true,
    think: false,
    keep_alive: '30m',
    options: { temperature: 0, num_predict: 250 },
  })
  // curl instead of $.http.fetch, which resolves only once the whole answer is in
  const curl = $.process.spawn({ argv: ['curl', '-sSN', '--fail-with-body', OLLAMA_URL, '-d', '@-'], input: body })
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

let timer: Timer | undefined
// Bumped on every edit, so a slow answer for an older draft never overwrites a newer one
let seq = 0
// Ollama answers one request at a time, so a check sent while another runs only queues behind it
let isRunning = false
let waiting: { draft: string; mine: number } | undefined

function cancelChecks() {
  timer?.cancel()
  seq += 1
  waiting = undefined
}

async function clear($: EngineInterface) {
  cancelChecks()
  await update($, check, () => null)
}

async function grammarCheck($: EngineInterface, draft: string, mine: number) {
  await update($, check, (prev): GrammarCheck => ({ status: 'checking', lines: prev?.lines ?? [] }))
  let lines: string[]
  try {
    lines = await runOllama($, draft, mine)
  } catch (error) {
    lines = [`ollama unreachable (${error instanceof Error ? error.message : String(error)})`]
  }
  if (mine === seq) {
    const result: GrammarCheck = { status: 'done', lines }
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

export const register: Register = on => {
  on('prompt.edit', async ($, e, next) => {
    const r = await next(e)
    if (r.text === e.text) {
      // A bare cursor move changes nothing worth checking
      return r
    }
    // Check a slash command's arguments, not the command name
    const draft = r.text.trim().replace(/^\/\S*\s*/, '')
    if (draft === '' || draft.startsWith('!')) {
      await clear($)
      return r
    }
    timer?.cancel()
    seq += 1
    const mine = seq
    timer = $.clock.after(DEBOUNCE_MS, () => {
      void requestCheck($, draft, mine)
    })
    return r
  })

  on('prompt.submit', async ($, e, next) => {
    cancelChecks()
    // Keep the last result on screen, dimmed, until the next draft is checked
    await update($, check, (prev): GrammarCheck | null => (prev?.status === 'done' ? { ...prev, status: 'submitted' } : null))
    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const current = await read($, check)
    if (e.props.hasSurvey || current === null) {
      return next(e)
    }

    const { Box, Text } = $.ui.resolve(e)
    const isChecking = current.status === 'checking' || current.status === 'streaming'
    const isDimmed = current.status === 'checking' || current.status === 'submitted'
    // Same colors as hal-statusline's colorize_grammar, except the label and explanation use the theme's text color: green for no issues, red otherwise
    const color = current.lines.some(line => line.toLowerCase().includes('no issues')) ? 'green' : 'red'

    return (
      // The glyph gets its own column: in a proportional font "⏺ " is not two cells wide, so padding would misalign the lines
      <Box flexDirection="row" marginTop={1}>
        <Box width={2}>
          <Text dimColor={isDimmed}>⏺</Text>
        </Box>
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
