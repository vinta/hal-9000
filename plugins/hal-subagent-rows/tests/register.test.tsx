import { describe, expect, test } from 'claude-code/testing'
import type { AgentInfo } from 'claude-code'

import { agentRowBody } from '../hooks/register'

const PLUGIN = 'hal-subagent-rows'
const ANSI = /\x1b\[[0-9;]*m/g

function makeAgent(overrides: Partial<AgentInfo> = {}): AgentInfo {
  return {
    id: 'agent-1',
    name: 'hal-skills-commit',
    description: '/hal-skills:commit all pending changes',
    type: 'general-purpose',
    status: 'running',
    kind: 'local_agent',
    taskStatus: 'running',
    label: 'commit',
    startTime: 1754000000000,
    cwd: '/usr/local/hal-9000',
    model: 'claude-sonnet-5',
    effort: 'high',
    contextWindowSize: 200000,
    tokenCount: 24000,
    tokenSamples: [],
    hasRow: true,
    ...overrides,
  }
}

function plain(body: string | undefined) {
  return body?.replace(ANSI, '')
}

describe('agentRowBody', () => {
  test('renders a full row', () => {
    expect(plain(agentRowBody(makeAgent(), 120))).toBe('hal-skills-commit (general-purpose) · working · sonnet-5 high · Context 12%')
  })

  test('colors only the model blue and the context by usage', () => {
    const separator = ' \x1b[37m·\x1b[0m '
    expect(agentRowBody(makeAgent(), 120)).toBe(`hal-skills-commit (general-purpose)${separator}\x1b[33mworking\x1b[0m${separator}\x1b[34msonnet-5 high\x1b[0m${separator}\x1b[32mContext 12%\x1b[0m`)
  })

  test('omits an inherited effort', () => {
    expect(plain(agentRowBody(makeAgent({ effort: undefined }), 120))).toBe('hal-skills-commit (general-purpose) · working · sonnet-5 · Context 12%')
  })

  test('marks a running agent with flat token samples as waiting', () => {
    expect(plain(agentRowBody(makeAgent({ tokenSamples: [5, 5, 5, 5, 5, 5] }), 120))).toContain(' · waiting · ')
  })

  test('shows an ended status as is', () => {
    expect(plain(agentRowBody(makeAgent({ status: 'completed' }), 120))).toContain(' · completed · ')
  })

  test('truncates the title to the columns', () => {
    const body = plain(agentRowBody(makeAgent(), 67))
    expect(body).toBe('hal-skil… (general-purpose) · working · sonnet-5 high · Context 12%')
    expect(body?.length).toBe(67)
  })

  test('drops the title when no room is left', () => {
    expect(plain(agentRowBody(makeAgent(), 58))).toBe('(general-purpose) · working · sonnet-5 high · Context 12%')
  })

  test('renders a numeric effort budget verbatim', () => {
    expect(plain(agentRowBody(makeAgent({ effort: 50000 }), 120))).toContain('sonnet-5 50000')
  })

  test('leads with the description when the agent has no name', () => {
    const agent = makeAgent({ name: undefined, effort: undefined, type: 'Explore', model: 'claude-opus-5[1m]', contextWindowSize: 1000000, tokenCount: 28261, description: 'List repo files' })
    expect(plain(agentRowBody(agent, 120))).toBe('List repo files (explore) · working · opus-5[1m] · Context 2%')
  })

  test('falls back to the label when the description is empty', () => {
    expect(plain(agentRowBody(makeAgent({ name: undefined, description: '' }), 120))).toBe('commit (general-purpose) · working · sonnet-5 high · Context 12%')
  })

  test('keeps a running agent working until 6 samples are flat', () => {
    for (const tokenSamples of [[100, 100, 100, 100, 100], [100, 100, 100, 100, 100, 200]]) {
      expect(plain(agentRowBody(makeAgent({ tokenSamples }), 120))).toContain(' · working · ')
    }
  })

  test('leaves the title whole when columns are unknown', () => {
    expect(plain(agentRowBody(makeAgent(), undefined))).toBe('hal-skills-commit (general-purpose) · working · sonnet-5 high · Context 12%')
  })

  test('draws nothing before the model resolves', () => {
    expect(agentRowBody(makeAgent({ model: undefined, contextWindowSize: undefined }), 120)).toBeUndefined()
  })
})

for (const surface of ['terminal', 'desktop'] as const) {
  test(`hands the engine the row body on ${surface}`, async ($, on) => {
    const bodies: (string | undefined)[] = []
    on('ui.render', ($, e) => {
      if (e.component === 'AgentRow') {
        bodies.push(e.props.body)
      }
      const { Text } = $.ui.resolve(e)
      return <Text>engine</Text>
    })

    const resolved = { ...makeAgent(), rowIds: ['agent-1', 'agent-2'], columns: 120, isHidden: false }
    const unresolved = { ...resolved, id: 'agent-2', model: undefined, contextWindowSize: undefined }
    for (const props of [resolved, unresolved]) {
      const ui = await $.ui.mount({ plugin: PLUGIN, surface, component: 'AgentRow', requestId: props.id, props })
      expect((await ui.find({ type: 'Text', text: 'engine' }))?.text).toBe('engine')
      await ui.unmount()
    }

    expect(bodies.map(plain)).toEqual(['hal-skills-commit (general-purpose) · working · sonnet-5 high · Context 12%', undefined])
  })
}
