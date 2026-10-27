import type { EngineInterface, Register } from 'claude-code'

// The desktop app already offers the reply's `!` command to run, so a suggestion there would duplicate it
const DESKTOP_ENTRYPOINTS = new Set(['claude-desktop', 'claude-desktop-3p'])

const SHELL_COMMAND = /`(![^`\n]+)`|^[ \t]*(!.+)$/m

const parse = (answer: string) => {
  const match = SHELL_COMMAND.exec(answer)

  return (match?.[1] ?? match?.[2])?.trimEnd()
}

const bashInput = (text: string) => text.slice('<bash-input>'.length, text.indexOf('</bash-input>')).trim()

function suggestLine($: EngineInterface, text: string | undefined) {
  if (text !== undefined) {
    // The engine refuses $.prompt.suggest while a turn runs, and this hook runs inside it.
    void $.clock.after(300, () => void $.prompt.suggest({ text }))
  }
}

export const register: Register = on => {
  let pending: string | undefined
  let isDesktop = false

  on('turn.complete', ($, e, next) => {
    if (isDesktop) {
      return next(e)
    }

    if (e.agentId === undefined && e.reason === 'answer') {
      const line = parse(e.answer)

      if (line !== undefined) {
        pending = line
      }

      suggestLine($, pending)
    }

    return next(e)
  })

  on('session.start', async ($, e, next) => {
    isDesktop = DESKTOP_ENTRYPOINTS.has((await $.env.get('CLAUDE_CODE_ENTRYPOINT')) ?? '')

    if (isDesktop) {
      return next(e)
    }

    // Replay the transcript through the same rules the live hooks apply.
    for (const { role, text } of await $.session.messages()) {
      if (role === 'assistant') {
        const line = parse(text)

        if (line !== undefined) {
          pending = line
        }
      } else if (text.startsWith('<bash-input>')) {
        if (bashInput(text) === pending?.slice(1).trim()) {
          pending = undefined
        }
      } else if (text !== '' && !text.startsWith('<')) {
        pending = undefined
      }
    }

    suggestLine($, pending)

    return next(e)
  })

  on('session.append', { door: 'command' }, ($, e, next) => {
    const text = e.message.content[0]?.text

    if (typeof text === 'string' && text.startsWith('<bash-input>')) {
      if (bashInput(text) === pending?.slice(1).trim()) {
        pending = undefined
      }
    }

    return next(e)
  })

  on('prompt.submit', ($, e, next) => {
    if (e.origin.kind === 'composer') {
      pending = undefined
    }

    return next(e)
  })

  on('prompt.suggest', ($, e, next) => {
    return pending !== undefined && e.origin.kind === 'suggestion' ? next({ ...e, text: pending }) : next(e)
  })
}
