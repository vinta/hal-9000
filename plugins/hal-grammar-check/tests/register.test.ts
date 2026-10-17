import { expect, mock, test } from 'claude-code/testing'
import type { PromptChangeInput, PromptChangeResult } from 'claude-code'

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

test('a model without a known backend fails the load', { options: { model: 'gpt-4' } }, async ($, on) => {
  on('prompt.change', ($, e) => ({ text: e.text }))

  await expect(change($)).rejects.toThrow('model "gpt-4" must be claude/<alias or id> or ollama/<model>')
})
