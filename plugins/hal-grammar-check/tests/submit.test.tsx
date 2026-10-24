import { expect, mock, test } from 'claude-code/testing'
import type { Engine, Mounted } from 'claude-code/testing'
import type { On, PromptChangeInput, PromptChangeResult } from 'claude-code'

const USAGE = { input_tokens: 0, output_tokens: 0, cache_creation_input_tokens: 0, cache_read_input_tokens: 0 }
const DRAFT: PromptChangeInput = { text: 'I has a apple', cursor: 13, origin: { kind: 'history' } }
const ABOVE_PROMPT = { hasSurvey: false, isWorking: true, maxRows: 10, bodyColumns: 80, scroll: { offset: 0, bodyRows: 10 }, view: {} }

// The kit raises prompt.change, but its Engine type leaves the event out
function change($: unknown, e: PromptChangeInput) {
  return ($ as { prompt: { change: (e: PromptChangeInput) => Promise<PromptChangeResult> } }).prompt.change(e)
}

function submit($: Engine) {
  return $.prompt.submit({ text: DRAFT.text, wait: false, origin: { kind: 'composer' } })
}

function setup(on: On, answer: () => Promise<void> | void = () => {}) {
  on('prompt.change', ($, e) => ({ text: e.text }))
  on('prompt.submit', ($, e) => ({ text: e.text }))
  on('ui.render', ($, e) => {
    const { Box } = $.ui.resolve(e)
    return <Box />
  })
  on('model.complete', async ($, e) => {
    await answer()
    const text = e.prompt.includes(DRAFT.text) ? 'I "have" an apple => x' : 'no issues'
    return { value: { isAnswered: true, text, usage: USAGE } }
  })
  return mock.clock(on)
}

function mount($: Engine) {
  return $.ui.mount({ plugin: 'hal-grammar-check', surface: 'terminal', component: 'AbovePrompt', props: ABOVE_PROMPT })
}

async function shownFix(band: Mounted<'terminal', 'AbovePrompt'>) {
  await band.redraw(ABOVE_PROMPT)
  return band.find({ type: 'Text', text: 'I have an apple => x' })
}

test('a draft sent before the debounce fires is still checked, dimmed', { options: { model: 'claude/haiku' } }, async ($, on) => {
  const clock = setup(on)
  const band = await mount($)

  await change($, DRAFT)
  await clock.advance(100)
  await submit($)

  expect(await shownFix(band)).toMatchObject({ props: { dimColor: true } })
})

test('a check in flight when the draft is sent lands dimmed', { options: { model: 'claude/haiku' } }, async ($, on) => {
  let release!: () => void
  const answered = new Promise<void>(resolve => (release = resolve))
  const clock = setup(on, () => answered)
  const band = await mount($)

  await change($, DRAFT)
  void clock.advance(250)
  await submit($)
  release()
  await clock.advance(0)

  expect(await shownFix(band)).toMatchObject({ props: { dimColor: true } })
})

test('typing a new draft drops the sent draft\'s answer', { options: { model: 'claude/haiku' } }, async ($, on) => {
  let release!: () => void
  const answered = new Promise<void>(resolve => (release = resolve))
  const clock = setup(on, () => answered)
  const band = await mount($)

  await change($, DRAFT)
  void clock.advance(250)
  await submit($)
  await change($, { text: 'Next', cursor: 4, origin: { kind: 'history' } })
  release()
  await clock.advance(250)

  expect(await shownFix(band)).toBeUndefined()
})
