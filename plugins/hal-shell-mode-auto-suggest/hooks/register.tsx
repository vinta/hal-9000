import type { EngineInterface, Register } from 'claude-code'

// The desktop app already offers the reply's `!` command to run, so a suggestion there would duplicate it
const DESKTOP_ENTRYPOINTS = new Set(['claude-desktop', 'claude-desktop-3p'])

const SHELL_COMMAND = /`(![^`\n]+)`|^[ \t]*(!.+)$/gm

const parse = (answer: string) =>
  [...answer.matchAll(SHELL_COMMAND)].map(match => (match[1] ?? match[2] ?? '').trimEnd())

function suggestHead($: EngineInterface, queue: string[]) {
  const text = queue[0]

  if (text !== undefined) {
    // The engine refuses $.prompt.suggest while a turn runs, and this hook runs inside it.
    void $.clock.after(300, () => void $.prompt.suggest({ text }))
  }
}

function popRun(queue: string[], text: string) {
  const input = text.slice('<bash-input>'.length, text.indexOf('</bash-input>')).trim()
  const index = queue.findIndex(entry => entry.slice(1).trim() === input)

  if (index >= 0) {
    queue.splice(index, 1)
  }
}

export const register: Register = on => {
  let queue: string[] = []
  let isDesktop = false

  on('turn.complete', ($, e, next) => {
    if (isDesktop) {
      return next(e)
    }

    if (e.agentId === undefined && e.reason === 'answer') {
      const lines = parse(e.answer)

      if (lines.length > 0) {
        queue = lines
      }

      suggestHead($, queue)
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
        const lines = parse(text)

        if (lines.length > 0) {
          queue = lines
        }
      } else if (text.startsWith('<bash-input>')) {
        popRun(queue, text)
      } else if (text !== '' && !text.startsWith('<')) {
        queue = []
      }
    }

    suggestHead($, queue)

    return next(e)
  })

  on('session.append', { door: 'command' }, ($, e, next) => {
    const text = e.message.content[0]?.text

    if (typeof text === 'string' && text.startsWith('<bash-input>')) {
      popRun(queue, text)
      suggestHead($, queue)
    }

    return next(e)
  })

  on('prompt.submit', ($, e, next) => {
    if (e.origin.kind === 'composer') {
      queue = []
    }

    return next(e)
  })

  on('prompt.suggest', ($, e, next) => {
    const head = queue[0]

    return head !== undefined && e.origin.kind === 'suggestion' ? next({ ...e, text: head }) : next(e)
  })
}
