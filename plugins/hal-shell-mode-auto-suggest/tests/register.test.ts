import { expect, mock, test } from 'claude-code/testing'
import type { Engine } from 'claude-code/testing'
import type { On } from 'claude-code'

const setUp = (on: On) => {
  const clock = mock.clock(on)
  const suggested: string[] = []
  on('turn.complete', (_, e) => ({ text: e.answer }))
  on('prompt.suggest', (_, e) => {
    suggested.push(e.text)

    return { isShown: true }
  })

  return { clock, suggested }
}

const complete = ($: Engine, answer: string, agentId?: string) =>
  $.turn.complete({
    answer,
    durationMs: 0,
    isAborted: false,
    turnId: 't1',
    reason: 'answer',
    ...(agentId === undefined ? {} : { agentId }),
  })

test('a `!` command in the answer becomes the suggestion', async ($, on) => {
  const { clock, suggested } = setUp(on)

  await complete($, 'To list the files, run `! ls -la` yourself.')
  await clock.advance(300)

  expect(suggested).toEqual(['! ls -la'])
})

test('an answer with no `!` command suggests nothing', async ($, on) => {
  const { clock, suggested } = setUp(on)

  await complete($, 'All done, `ls -la` shows the files.')
  await clock.advance(300)

  expect(suggested).toEqual([])
})

test("a subagent's turn is ignored", async ($, on) => {
  const { clock, suggested } = setUp(on)

  await complete($, 'Run `! ls -la`.', 'a1')
  await clock.advance(300)

  expect(suggested).toEqual([])
})

test("the engine's later guess is replaced by the command", async ($, on) => {
  const { clock, suggested } = setUp(on)

  await complete($, 'Run `! ls -la`.')
  await clock.advance(300)
  await $.prompt.suggest({ text: 'engine guess', origin: { kind: 'suggestion' } })

  expect(suggested).toEqual(['! ls -la', '! ls -la'])
})

test('the first of several plain `!` lines wins, verbatim', async ($, on) => {
  const { clock, suggested } = setUp(on)

  await complete(
    $,
    [
      'Remove the stale links:',
      '',
      "! sudo find /usr/local/bin -lname '*Python.framework/Versions/3.13/*' -delete  ",
      "! sudo rm -rf '/Library/Frameworks/Python.framework/Versions/3.13'",
      '! sudo pkgutil --forget org.python.Python.PythonFramework-3.13',
    ].join('\n'),
  )
  await clock.advance(300)

  expect(suggested).toEqual([
    "! sudo find /usr/local/bin -lname '*Python.framework/Versions/3.13/*' -delete",
  ])
})
