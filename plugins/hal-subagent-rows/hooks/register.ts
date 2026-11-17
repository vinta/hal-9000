import type { AgentInfo, Register } from 'claude-code'

const BLUE = '\x1b[34m'
const GREEN = '\x1b[32m'
const YELLOW = '\x1b[33m'
const RED = '\x1b[31m'
const WHITE = '\x1b[37m'
const RESET = '\x1b[0m'

const SEPARATOR = ` ${WHITE}·${RESET} `
const SEPARATOR_WIDTH = ' · '.length
const STATUS_COLORS: Record<string, string> = { working: YELLOW, waiting: WHITE, completed: GREEN, failed: RED, killed: RED }
// Token count flat across this many samples marks a running subagent as waiting, usually on a tool call
const WAIT_SAMPLES = 6

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
  let title = agent.name || agent.description || agent.label
  if (columns !== undefined) {
    const budget = columns - agentType.length - 1 - status.length - modelPart.length - ctxPlain.length - 3 * SEPARATOR_WIDTH
    if (title.length > budget) {
      title = budget >= 2 ? `${title.slice(0, budget - 1)}…` : ''
    }
  }
  parts.unshift(title ? `${title} ${agentType}` : agentType)

  return parts.join(SEPARATOR)
}

export const register: Register = (on) => {
  on('ui.render', { component: 'AgentRow' }, ($, e, next) => {
    const body = agentRowBody(e.props, e.props.columns)
    return next(body === undefined ? e : { ...e, props: { ...e.props, body } })
  })
}
