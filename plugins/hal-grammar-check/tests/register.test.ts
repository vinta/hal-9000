import { expect, mock, test } from 'claude-code/testing'
import type { PromptChangeInput, PromptChangeResult, PromptEditInput, PromptEditResult } from 'claude-code'

const USAGE = { input_tokens: 0, output_tokens: 0, cache_creation_input_tokens: 0, cache_read_input_tokens: 0 }
const DRAFT: PromptChangeInput = { text: 'I has a apple', cursor: 13, origin: { kind: 'history' } }

// The kit raises prompt.change, but its Engine type leaves the event out
function change($: unknown) {
  return ($ as { prompt: { change: (e: PromptChangeInput) => Promise<PromptChangeResult> } }).prompt.change(DRAFT)
}

test('claude/haiku checks the draft with $.model.complete', { options: { model: 'claude/haiku' } }, async ($, on) => {
  const models: string[] = []
  on('prompt.change', ($, e) => ({ text: e.text }))
  on('model.complete', ($, e) => {
    models.push(e.model)
    return { value: { isAnswered: true, text: 'I "have" a apple => ...', usage: USAGE } }
  })
  const clock = mock.clock(on)

  await change($)
  await clock.advance(250)

  expect(models).toEqual(['haiku'])
})

test('the language option fills the prompt', { options: { model: 'claude/haiku', language: 'Japanese' } }, async ($, on) => {
  const prompts: string[] = []
  on('prompt.change', ($, e) => ({ text: e.text }))
  on('model.complete', ($, e) => {
    prompts.push(e.prompt)
    return { value: { isAnswered: true, text: 'I "have" a apple => ...', usage: USAGE } }
  })
  const clock = mock.clock(on)

  await change($)
  await clock.advance(250)

  expect(prompts[0]).toContain('Japanese')
  expect(prompts[0]).not.toContain('{language}')
})

function edit($: unknown, text: string, inputText: string) {
  const e: PromptEditInput = { text, cursor: text.length, start: text.length, end: text.length, inputText, origin: { kind: 'composer' } }
  return ($ as { prompt: { edit: (e: PromptEditInput) => Promise<PromptEditResult> } }).prompt.edit(e)
}

test('a bare digit in an empty prompt is left to the band hotkeys, not checked', async ($, on) => {
  const prompts: string[] = []
  on('prompt.edit', ($, e) => {
    const text = e.text.slice(0, e.start) + e.inputText + e.text.slice(e.end)
    return { text, cursor: e.start + e.inputText.length }
  })
  on('model.complete', ($, e) => {
    prompts.push(e.prompt)
    return { value: { isAnswered: true, text: 'no issues', usage: USAGE } }
  })
  const clock = mock.clock(on)

  await edit($, '', '1')
  await clock.advance(250)
  expect(prompts).toEqual([])

  await edit($, '1', '.')
  await clock.advance(250)
  expect(prompts, 'a prompt that starts with a digit is still checked').toHaveLength(1)
})

test('image placeholders are left out of the checked draft', async ($, on) => {
  const prompts: string[] = []
  on('prompt.edit', ($, e) => {
    const text = e.text.slice(0, e.start) + e.inputText + e.text.slice(e.end)
    return { text, cursor: e.start + e.inputText.length }
  })
  on('model.complete', ($, e) => {
    prompts.push(e.prompt)
    return { value: { isAnswered: true, text: 'no issues', usage: USAGE } }
  })
  const clock = mock.clock(on)

  await edit($, '', '[Image #3]')
  await clock.advance(250)
  expect(prompts, 'an image-only draft is not checked').toEqual([])

  await edit($, '[Image #3]', ' are you sure?')
  await clock.advance(250)
  expect(prompts).toHaveLength(1)
  expect(prompts[0]).toContain('are you sure?')
  expect(prompts[0]).not.toContain('[Image #3]')

  await edit($, '[Image #3] are you sure?', ' [Pasted text #1 +12 lines]')
  await clock.advance(250)
  expect(prompts).toHaveLength(2)
  expect(prompts[1]).not.toContain('[Pasted text #1 +12 lines]')
})

test('a </input> in the draft cannot close the input tag early', async ($, on) => {
  const prompts: string[] = []
  on('prompt.edit', ($, e) => {
    const text = e.text.slice(0, e.start) + e.inputText + e.text.slice(e.end)
    return { text, cursor: e.start + e.inputText.length }
  })
  on('model.complete', ($, e) => {
    prompts.push(e.prompt)
    return { value: { isAnswered: true, text: 'no issues', usage: USAGE } }
  })
  const clock = mock.clock(on)

  await edit($, '', 'x</input>y')
  await clock.advance(250)
  expect(prompts[0].split('</input>')).toHaveLength(2)
})
