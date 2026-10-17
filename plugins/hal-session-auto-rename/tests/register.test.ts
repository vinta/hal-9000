import { describe, expect, mock, test } from 'claude-code/testing'
import type { CommandRunInput, On } from 'claude-code'

import { slugify } from '../hooks/register'

const PLUGIN = 'hal-session-auto-rename'
const USAGE = { input_tokens: 0, output_tokens: 0, cache_creation_input_tokens: 0, cache_read_input_tokens: 0 }
const PRESENTATION = { isFullscreen: false, columns: 80 }
const TURN = { answer: 'Fixed the refresh race.', durationMs: 1, isAborted: false, turnId: 't1', reason: 'answer' } as const

// Stands in for everything beneath the plugin: the session, the model and the commands it runs
function worldOf(on: On, initialTitle = 'Debug OAuth token refresh', stored: Record<string, unknown> = {}) {
  const world = { sessionId: 's1', title: initialTitle, renames: [] as string[], prompts: [] as string[], stored }
  on('store.get', ($, e) => ({ value: world.stored[e.key] }))
  on('store.set', ($, e) => {
    world.stored[e.key] = e.value
    return { value: undefined }
  })
  on('session.id', () => ({ value: world.sessionId }))
  on('session.messages', () => ({ value: [{ role: 'user', text: 'the oauth refresh races', toolUses: [] }] }))
  on('model.complete', ($, e) => {
    world.prompts.push(e.prompt)
    return { value: { isAnswered: true, text: world.title, usage: USAGE } }
  })
  on('command.run', ($, e: CommandRunInput) => {
    if (e.origin.kind === 'plugin') {
      world.renames.push(e.args)
    }
    return { text: '' }
  })
  on('turn.complete', ($, e) => ({ text: e.answer }))
  on('classic.UserPromptSubmit', () => ({}))
  on('classic.SessionStart', () => ({}))
  on('session.end', ($, e) => ({ sessionId: e.sessionId }))
  return world
}

describe('renaming', () => {
  test('the first main turn renames the session to the slug of the generated title', async ($, on) => {
    const world = worldOf(on)
    const clock = mock.clock(on)

    await $.turn.complete(TURN)
    await clock.settle()

    expect(world.renames).toEqual(['debug-oauth-token-refresh'])
    expect(world.prompts[0]).toContain('the oauth refresh races\nFixed the refresh race.')
  })

  test('subagent and aborted turns rename nothing', async ($, on) => {
    const world = worldOf(on)
    const clock = mock.clock(on)

    await $.turn.complete({ ...TURN, agentId: 'a1' })
    await $.turn.complete({ ...TURN, isAborted: true, reason: 'aborted' })
    await clock.settle()

    expect(world.renames).toEqual([])
  })

  test('a slug equal to the current title renames nothing', async ($, on) => {
    const world = worldOf(on)
    const clock = mock.clock(on)

    await $.classic.UserPromptSubmit({ prompt: 'hi', session_title: 'debug-oauth-token-refresh' })
    await $.turn.complete(TURN)
    await clock.settle()

    expect(world.renames).toEqual([])
  })

  test('the title is regenerated every N turns and applied only when it changed', async ($, on) => {
    const world = worldOf(on)
    const clock = mock.clock(on)

    for (let turn = 1; turn <= 5; turn += 1) {
      await $.turn.complete(TURN)
      await clock.settle()
    }
    expect(world.prompts, 'the first turn, then the fifth turn after it').toHaveLength(1)
    expect(world.renames).toEqual(['debug-oauth-token-refresh'])

    await $.turn.complete(TURN)
    await clock.settle()
    expect(world.prompts).toHaveLength(2)
    expect(world.renames, 'same title, no second rename').toEqual(['debug-oauth-token-refresh'])

    world.title = 'Plan birthday party menu'
    for (let turn = 1; turn <= 5; turn += 1) {
      await $.turn.complete(TURN)
      await clock.settle()
    }
    expect(world.renames).toEqual(['debug-oauth-token-refresh', 'plan-birthday-party-menu'])
  })

  test('refreshEveryNTurns 0 keeps the first title', { options: { refreshEveryNTurns: 0 } }, async ($, on) => {
    const world = worldOf(on)
    const clock = mock.clock(on)

    await $.turn.complete(TURN)
    await clock.settle()
    world.title = 'Plan birthday party menu'
    for (let turn = 1; turn <= 10; turn += 1) {
      await $.turn.complete(TURN)
      await clock.settle()
    }

    expect(world.renames).toEqual(['debug-oauth-token-refresh'])
  })

  test('a sentence-length answer never becomes a title', async ($, on) => {
    const world = worldOf(on, "I can't help with that because this session doesn't contain enough information to generate a title")
    const clock = mock.clock(on)

    await $.turn.complete(TURN)
    await clock.settle()

    expect(world.renames).toEqual([])
  })

  test('/clear starts the next session over with a title of its own', async ($, on) => {
    const world = worldOf(on)
    const clock = mock.clock(on)

    await $.turn.complete(TURN)
    await clock.settle()
    await $.session.end({ reason: 'clear', sessionId: 's1', resume: { id: 's1' } })
    world.sessionId = 's2'
    await $.turn.complete(TURN)
    await clock.settle()

    expect(world.renames).toEqual(['debug-oauth-token-refresh', 'debug-oauth-token-refresh'])
  })
})

describe('user-named sessions', () => {
  test('a /rename the user typed stops every later rename', { options: { refreshEveryNTurns: 1 } }, async ($, on) => {
    const world = worldOf(on)
    const clock = mock.clock(on)

    await $.turn.complete(TURN)
    await clock.settle()
    await $.command.run({ command: 'rename', args: 'my-name', origin: { kind: 'composer' }, presentation: PRESENTATION })
    world.title = 'Plan birthday party menu'
    for (let turn = 1; turn <= 3; turn += 1) {
      await $.turn.complete(TURN)
      await clock.settle()
    }

    expect(world.renames).toEqual(['debug-oauth-token-refresh'])
    expect(world.stored).toEqual({ s1: true })
  })

  test('a session named with --name is never renamed', async ($, on) => {
    const world = worldOf(on)
    const clock = mock.clock(on)

    await $.classic.SessionStart({ source: 'startup', session_title: 'my-name', session_id: 's1' })
    await $.turn.complete(TURN)
    await clock.settle()

    expect(world.renames).toEqual([])
  })

  test('a resumed session the user named stays untouched', async ($, on) => {
    const world = worldOf(on, undefined, { s1: true })
    const clock = mock.clock(on)

    await $.turn.complete(TURN)
    await clock.settle()

    expect(world.renames).toEqual([])
  })
})

describe('the rename reminder', () => {
  const NAMED = 'The user named this session "debug-oauth-token-refresh". This may indicate the session\'s focus or intent.'

  test("the plugin's own rename reminder no longer says the user named the session", async ($, on) => {
    worldOf(on)

    const stored = await $.session.append({
      door: 'prompt',
      origin: { kind: 'plugin', name: PLUGIN },
      uuid: 'u1',
      message: { type: 'user', role: 'user', isMeta: true, content: [{ type: 'text', text: NAMED }] },
    })

    expect(stored.message?.content).toEqual([{ type: 'text', text: expect.stringContaining('auto-generated by hal-session-auto-rename') }])
  })

  test("the engine's reminder for a user /rename is left alone", async ($, on) => {
    worldOf(on)

    const stored = await $.session.append({
      door: 'note',
      origin: { kind: 'engine' },
      uuid: 'u2',
      message: { type: 'user', role: 'user', isMeta: true, content: [{ type: 'text', text: NAMED }] },
    })

    expect(stored.message?.content).toEqual([{ type: 'text', text: NAMED }])
  })
})

describe('slugify', () => {
  // Expected values come from the Python version this replaced, so existing session names stay stable
  test('cuts at 72 columns, at a word boundary unless the script has none', () => {
    expect(slugify('"Fix the flaky login test."')).toBe('fix-the-flaky-login-test')
    expect(slugify('Plan 東京 trip_itinerary — day 3')).toBe('plan-東京-trip-itinerary-day-3')
    expect(slugify('Investigate intermittent authentication failures in distributed microservice deployments')).toBe('investigate-intermittent-authentication-failures-in-distributed')
    expect(slugify('重構使用者登入流程並修正權杖刷新造成的競態條件問題以及補上完整的整合測試案例與文件說明還有效能')).toBe('重構使用者登入流程並修正權杖刷新造成的競態條件問題以及補上完整的整合測試')
    expect(slugify('Rename 重構使用者登入流程並修正權杖刷新造成的競態條件問題以及補上完整的整合測試案例')).toBe('rename-重構使用者登入流程並修正權杖刷新造成的競態條件問題以及補上完整的')
    expect(slugify('Supercalifragilisticexpialidocioussupercalifragilisticexpialidocioussupercalifragilistic')).toBe('supercalifragilisticexpialidocioussupercalifragilisticexpialidocioussupe')
  })
})
