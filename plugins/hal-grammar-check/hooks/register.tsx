import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register, Timer } from 'claude-code'

import type { GrammarCheck } from '../types'

const check = atom({ plugin: 'hal-grammar-check', key: 'check' } as const, null)

const DEBOUNCE_MS = 800
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
- Each issue on its own line: Grammar: "[corrected]" => explanation in Traditional Chinese
- Use full-width commas (，) in Chinese explanations
- No errors: output exactly "Grammar: no issues"
- Output ONLY the "Grammar: ..." line(s). No commentary, no extra text, no explanations beyond the correction format above.
</instructions>

<examples>
<example>
Text: I don't car the shop has wife or not. I will use cellar!
Output:
Grammar: I don't "care" => car 是「汽車」，這裡應該是要用動詞 care「在乎」
Grammar: has "Wi-Fi" or not => wife 是「妻子」，你是要說 Wi-Fi「無線網路」吧？
Grammar: I will use "cellular" => cellar 是「地窖」，這裡應該是 cellular「行動網路」
</example>
<example>
Text: @plugins/hal-statusline/hal-statusline.py#L141 use \`claude -p\` and \`grammar_check_prompt\` to grammar check \`latest_user_input\` and print result
Output:
Grammar: to "grammar-check" latest_user_input => 要用連字號 "-" 連接形成複合動詞
Grammar: print "the" result => result 前面要加定冠詞 the
</example>
<example>
Text: The code is works but I don't know why it keep crashing
Output:
Grammar: The code "works" => 不需要 is，直接用動詞 works；或改成 is working
Grammar: why it "keeps" crashing => 第三人稱單數 it 要用 keeps
</example>
<example comment="skip Capitalization at sentence beginnings (lowercase 'do' is excluded per instruction)">
Text: do not refactor unless explicited requested
Output:
Grammar: "explicitly requested" => 要用副詞 explicitly，沒有 explicited 這個詞
</example>
<example comment="skip Capitalization (lowercase pronoun 'i' and sentence-start 'check' are excluded per instruction)">
Text: Wait, i seems broke it. check codebase again
Output:
Grammar: I "seem to have broken" it => 用 seem to have + 過去分詞表示「好像已經...」
Grammar: Check "the" codebase => 特指這個 codebase，要加定冠詞 the
</example>
<example comment="skip Capitalization at sentence beginnings; demonstrate 'no issues' output">
Text: can you review my PR?
Output:
Grammar: no issues
</example>
</examples>

<input>
{latest_user_input}
</input>
`

async function runOllama($: EngineInterface, draft: string): Promise<string[]> {
  // `think: false` disables reasoning tokens; `temperature: 0` and `num_predict` keep the output short
  const body = JSON.stringify({
    model: OLLAMA_MODEL,
    prompt: GRAMMAR_PROMPT.replace('{latest_user_input}', draft.slice(0, 500)),
    stream: false,
    think: false,
    keep_alive: '30m',
    options: { temperature: 0, num_predict: 250 },
  })
  const res = await $.http.fetch(OLLAMA_URL, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body })
  if (!res.ok) {
    return [`Grammar: ollama answered HTTP ${res.status}`]
  }
  const { response } = JSON.parse(res.text) as { response: string }
  return response.split('\n').map(line => line.trim()).filter(Boolean)
}

let timer: Timer | undefined
// Bumped on every edit, so a slow answer for an older draft never overwrites a newer one
let seq = 0

async function clear($: EngineInterface) {
  timer?.cancel()
  seq += 1
  await update($, check, () => null)
}

async function grammarCheck($: EngineInterface, draft: string, mine: number) {
  await update($, check, (prev): GrammarCheck => ({ status: 'checking', lines: prev?.lines ?? [] }))
  let lines: string[]
  try {
    lines = await runOllama($, draft)
  } catch (error) {
    lines = [`Grammar: ollama unreachable (${error instanceof Error ? error.message : String(error)})`]
  }
  if (mine === seq) {
    const result: GrammarCheck = { status: 'done', lines }
    await update($, check, () => result)
  }
}

export const register: Register = on => {
  on('prompt.edit', async ($, e, next) => {
    const r = await next(e)
    if (r.text === e.text) {
      // A bare cursor move changes nothing worth checking
      return r
    }
    const draft = r.text.trim()
    if (draft === '' || draft.startsWith('/') || draft.startsWith('!')) {
      await clear($)
      return r
    }
    timer?.cancel()
    seq += 1
    const mine = seq
    timer = $.clock.after(DEBOUNCE_MS, () => {
      void grammarCheck($, draft, mine)
    })
    return r
  })

  on('prompt.submit', async ($, e, next) => {
    await clear($)
    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const current = await read($, check)
    if (e.props.hasSurvey || current === null || current.lines.length === 0) {
      return next(e)
    }

    const { Box, Text } = $.ui.resolve(e)
    const isChecking = current.status === 'checking'

    return (
      <Box flexDirection="column">
        {current.lines.map((line, i) => (
          <Text key={`line-${i}`} dimColor={isChecking || line.endsWith('no issues')} color={isChecking ? undefined : 'warning'}>
            {line}
          </Text>
        ))}
      </Box>
    )
  })
}
