import { describe, expect, test } from 'claude-code/testing'
import type { AgentInfo } from 'claude-code'

import { agentRowBody } from '../hooks/register'

const PLUGIN = 'hal-subagent-rows'
const ANSI = /\x1b\[[0-9;]*m/g
const START = 1754000000000
// 1m42s after the fixture agent started
const NOW = START + 102_000

function makeAgent(overrides: Partial<AgentInfo> = {}): AgentInfo {
  return {
    id: 'agent-1',
    name: 'hal-skills-commit',
    description: '/hal-skills:commit all pending changes',
    type: 'general-purpose',
    status: 'running',
    kind: 'local_agent',
    taskStatus: 'running',
    label: '/hal-skills:commit all pending changes',
    startTime: START,
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

function row(agent: AgentInfo, columns: number | undefined) {
  return agentRowBody(agent, columns, NOW)
}

function plain(body: string | undefined) {
  return body?.replace(ANSI, '')
}

describe('agentRowBody', () => {
  test('renders a full row', () => {
    expect(plain(row(makeAgent(), 120))).toBe('hal-skills-commit (general-purpose) · 1m42s · working · sonnet-5 high · Context 12%')
  })

  test('colors only the model blue and the context by usage', () => {
    const separator = ' \x1b[37m·\x1b[0m '
    expect(row(makeAgent(), 120)).toBe(`hal-skills-commit (general-purpose)${separator}1m42s${separator}\x1b[33mworking\x1b[0m${separator}\x1b[34msonnet-5 high\x1b[0m${separator}\x1b[32mContext 12%\x1b[0m`)
  })

  test('omits an inherited effort', () => {
    expect(plain(row(makeAgent({ effort: undefined }), 120))).toBe('hal-skills-commit (general-purpose) · 1m42s · working · sonnet-5 · Context 12%')
  })

  test('marks a running agent with flat token samples as waiting', () => {
    expect(plain(row(makeAgent({ tokenSamples: [5, 5, 5, 5, 5, 5] }), 120))).toContain(' · waiting · ')
  })

  test('shows an ended status as is', () => {
    expect(plain(row(makeAgent({ status: 'completed' }), 120))).toContain(' · completed · ')
  })

  test('truncates the title to the columns', () => {
    const body = plain(row(makeAgent(), 75))
    expect(body).toBe('hal-skil… (general-purpose) · 1m42s · working · sonnet-5 high · Context 12%')
    expect(body?.length).toBe(75)
  })

  test('drops the title when no room is left', () => {
    expect(plain(row(makeAgent(), 66))).toBe('(general-purpose) · 1m42s · working · sonnet-5 high · Context 12%')
  })

  test('renders a numeric effort budget verbatim', () => {
    expect(plain(row(makeAgent({ effort: 50000 }), 120))).toContain('sonnet-5 50000')
  })

  test('leads with the description when the agent has no name', () => {
    const agent = makeAgent({ name: undefined, effort: undefined, type: 'Explore', model: 'claude-opus-5[1m]', contextWindowSize: 1000000, tokenCount: 28261, description: 'List repo files', label: 'List repo files' })
    expect(plain(row(agent, 120))).toBe('List repo files (explore) · 1m42s · working · opus-5[1m] · Context 2%')
  })

  test('falls back to the label when the description is empty', () => {
    expect(plain(row(makeAgent({ name: undefined, description: '', label: 'commit' }), 120))).toBe('commit (general-purpose) · 1m42s · working · sonnet-5 high · Context 12%')
  })

  test('keeps a running agent working until 6 samples are flat', () => {
    for (const tokenSamples of [[100, 100, 100, 100, 100], [100, 100, 100, 100, 100, 200]]) {
      expect(plain(row(makeAgent({ tokenSamples }), 120))).toContain(' · working · ')
    }
  })

  test('leaves the title whole when columns are unknown', () => {
    expect(plain(row(makeAgent(), undefined))).toBe('hal-skills-commit (general-purpose) · 1m42s · working · sonnet-5 high · Context 12%')
  })

  test('adds the progress summary as a gray second line', () => {
    expect(row(makeAgent({ label: 'Reading register.ts' }), 120)).toMatch(/\n\x1b\[90mReading register\.ts\x1b\[0m$/)
  })

  test('shows only the first non-empty line of the progress summary', () => {
    expect(plain(row(makeAgent({ label: '\nReading register.ts\nthen the tests' }), 120))?.split('\n')[1]).toBe('Reading register.ts')
  })

  test('truncates the progress summary to the columns', () => {
    expect(plain(row(makeAgent({ label: 'Reading every register file in the repo' }), 20))?.split('\n')[1]).toBe('Reading every regis…')
  })

  test('fits a wide-character title by terminal columns', () => {
    expect(plain(row(makeAgent({ name: '審查所有外掛程式的掛鉤設定' }), 78))).toBe('審查所有外… (general-purpose) · 1m42s · working · sonnet-5 high · Context 12%')
  })

  test('fits a wide-character progress summary by terminal columns', () => {
    expect(plain(row(makeAgent({ label: '讀取外掛程式的掛鉤設定檔' }), 20))?.split('\n')[1]).toBe('讀取外掛程式的掛鉤…')
  })

  test('formats the elapsed time by its largest unit', () => {
    for (const [ms, elapsed] of [[42_000, '42s'], [185_000, '3m05s'], [3_780_000, '1h03m']] as const) {
      expect(plain(agentRowBody(makeAgent(), undefined, START + ms))).toContain(` · ${elapsed} · working · `)
    }
  })

  test('leaves the elapsed time off an ended agent', () => {
    expect(plain(row(makeAgent({ status: 'killed' }), 120))).toBe('hal-skills-commit (general-purpose) · killed · sonnet-5 high · Context 12%')
  })

  test('draws nothing before the model resolves', () => {
    expect(row(makeAgent({ model: undefined, contextWindowSize: undefined }), 120)).toBeUndefined()
  })
})

for (const surface of ['terminal', 'desktop'] as const) {
  test(`hands the engine the row body on ${surface}`, async ($, on) => {
    const bodies: (string | undefined)[] = []
    on('clock.now', () => ({ value: NOW }))
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

    expect(bodies.map(plain)).toEqual(['hal-skills-commit (general-purpose) · 1m42s · working · sonnet-5 high · Context 12%', undefined])
  })

  test(`narrows a nested row by 2 columns per level on ${surface}`, async ($, on) => {
    const titles: (string | undefined)[] = []
    on('clock.now', () => ({ value: NOW }))
    on('agent.list', () => ({ value: [makeAgent({ id: 'root' }), makeAgent({ id: 'middle', parentId: 'root' })] }))
    on('ui.render', ($, e) => {
      if (e.component === 'AgentRow') {
        titles.push(plain(e.props.body)?.split(' (')[0])
      }
      const { Text } = $.ui.resolve(e)
      return <Text>engine</Text>
    })

    const base = { ...makeAgent(), rowIds: ['root', 'middle', 'leaf'], columns: 75, isHidden: false }
    for (const props of [base, { ...base, id: 'middle', parentId: 'root' }, { ...base, id: 'leaf', parentId: 'middle' }]) {
      const ui = await $.ui.mount({ plugin: PLUGIN, surface, component: 'AgentRow', requestId: props.id, props })
      await ui.unmount()
    }

    expect(titles).toEqual(['hal-skil…', 'hal-sk…', 'hal-…'])
  })

  test(`starts the elapsed-time ticker for a live row only on ${surface}`, async ($, on) => {
    const periods: number[] = []
    on('clock.now', () => ({ value: NOW }))
    // A refused period ends the interval, so the test sees the ticker start without it looping
    on('clock.every', (_, e) => {
      periods.push(e.ms)
      return { deny: 'test' }
    })
    on('ui.render', ($, e) => {
      const { Text } = $.ui.resolve(e)
      return <Text>engine</Text>
    })

    const ended = { ...makeAgent({ status: 'killed' }), rowIds: ['agent-1'], columns: 120, isHidden: false }
    for (const props of [ended, { ...ended, status: 'running' as const }]) {
      const ui = await $.ui.mount({ plugin: PLUGIN, surface, component: 'AgentRow', requestId: props.id, props })
      await ui.unmount()
      if (props.status === 'killed') {
        expect(periods).toEqual([])
      }
    }

    expect(periods).toEqual([1000])
  })
}
