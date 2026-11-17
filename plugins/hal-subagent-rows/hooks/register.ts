import type { AgentInfo, EngineInterface, Register } from 'claude-code'

const BLUE = '\x1b[34m'
const GREEN = '\x1b[32m'
const YELLOW = '\x1b[33m'
const RED = '\x1b[31m'
const WHITE = '\x1b[37m'
const GRAY = '\x1b[90m'
const RESET = '\x1b[0m'

const SEPARATOR = ` ${WHITE}·${RESET} `
const SEPARATOR_WIDTH = ' · '.length
const STATUS_COLORS: Record<string, string> = { working: YELLOW, waiting: WHITE, completed: GREEN, failed: RED, killed: RED }
// Token count flat across this many samples marks a running subagent as waiting, usually on a tool call
const WAIT_SAMPLES = 6
// A nested row's tree connector takes this many of the top-level row's columns per level
const NESTING_COLUMNS = 2
// East Asian Wide and Fullwidth ranges after Markus Kuhn's mk_wcwidth, plus the emoji blocks terminals draw two columns wide
const WIDE_RANGES = [
  [0x1100, 0x115f],
  [0x2329, 0x232a],
  [0x2e80, 0x303e],
  [0x3040, 0xa4cf],
  [0xac00, 0xd7a3],
  [0xf900, 0xfaff],
  [0xfe10, 0xfe19],
  [0xfe30, 0xfe6f],
  [0xff00, 0xff60],
  [0xffe0, 0xffe6],
  [0x1f300, 0x1f64f],
  [0x1f900, 0x1f9ff],
  [0x20000, 0x2fffd],
  [0x30000, 0x3fffd],
] as const

function charColumns(char: string) {
  const codePoint = char.codePointAt(0) ?? 0
  return WIDE_RANGES.some(([low, high]) => codePoint >= low && codePoint <= high) ? 2 : 1
}

function columnWidth(text: string) {
  let width = 0
  for (const char of text) {
    width += charColumns(char)
  }
  return width
}

function fitColumns(text: string, columns: number) {
  if (columnWidth(text) <= columns) {
    return text
  }
  let head = ''
  let width = 0
  for (const char of text) {
    width += charColumns(char)
    if (width > columns - 1) {
      break
    }
    head += char
  }
  return `${head}…`
}

function usageColor(pct: number) {
  return pct >= 90 ? RED : pct >= 70 ? YELLOW : GREEN
}

function agentState(agent: AgentInfo) {
  if (agent.status !== 'running') {
    return agent.status
  }
  const recent = agent.tokenSamples.slice(-WAIT_SAMPLES)
  return recent.length === WAIT_SAMPLES && new Set(recent).size === 1 ? 'waiting' : 'working'
}

export function agentRowBody(agent: AgentInfo, columns: number | undefined) {
  if (agent.model === undefined || agent.contextWindowSize === undefined) {
    return undefined
  }
  const model = agent.model.replace(/^claude-/, '')
  const modelPart = agent.effort === undefined ? model : `${model} ${agent.effort}`

  const ctxPct = Math.floor((agent.tokenCount / agent.contextWindowSize) * 100)
  const ctxPlain = `Context ${ctxPct}%`
  const status = agentState(agent)
  const parts = [`${STATUS_COLORS[status] ?? WHITE}${status}${RESET}`, `${BLUE}${modelPart}${RESET}`, `${usageColor(ctxPct)}${ctxPlain}${RESET}`]

  const agentType = `(${agent.type.toLowerCase()})`
  const fullTitle = agent.name || agent.description || agent.label
  let title = fullTitle
  if (columns !== undefined) {
    const budget = columns - agentType.length - 1 - status.length - modelPart.length - ctxPlain.length - 3 * SEPARATOR_WIDTH
    if (columnWidth(title) > budget) {
      title = budget >= 2 ? fitColumns(title, budget) : ''
    }
  }
  parts.unshift(title ? `${title} ${agentType}` : agentType)
  const row = parts.join(SEPARATOR)

  // label falls back to description until the engine stores a progress summary
  let progress = agent.label.split('\n').find((line) => line.trim())?.trim()
  if (!progress || progress === agent.description || progress === fullTitle) {
    return row
  }
  if (columns !== undefined) {
    progress = fitColumns(progress, columns)
  }
  return `${row}\n${GRAY}${progress}${RESET}`
}

async function nestingDepth($: EngineInterface, agent: AgentInfo) {
  if (agent.parentId === undefined) {
    return 0
  }
  const parentIds = new Map((await $.agent.list()).map((listed) => [listed.id, listed.parentId]))
  let depth = 0
  for (let id: string | undefined = agent.parentId; id !== undefined; id = parentIds.get(id)) {
    depth += 1
  }
  return depth
}

export const register: Register = (on) => {
  on('ui.render', { component: 'AgentRow' }, async ($, e, next) => {
    const columns = e.props.columns === undefined ? undefined : e.props.columns - NESTING_COLUMNS * (await nestingDepth($, e.props))
    const body = agentRowBody(e.props, columns)
    return next(body === undefined ? e : { ...e, props: { ...e.props, body } })
  })
}
