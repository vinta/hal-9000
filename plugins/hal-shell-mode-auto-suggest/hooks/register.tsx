import type { Register } from 'claude-code'

const SHELL_COMMAND = /`(![^`\n]+)`|^[ \t]*(!.+)$/m

const parse = (answer: string) => {
  const match = SHELL_COMMAND.exec(answer)

  return (match?.[1] ?? match?.[2])?.trimEnd()
}

export const register: Register = on => {
  let pending: string | undefined

  on('turn.complete', ($, e, next) => {
    if (e.agentId === undefined) {
      pending = e.reason === 'answer' ? parse(e.answer) : undefined
      const text = pending

      if (text !== undefined) {
        // The engine refuses $.prompt.suggest while a turn runs, and this hook runs inside it.
        void $.clock.after(300, () => void $.prompt.suggest({ text }))
      }
    }

    return next(e)
  })

  on('prompt.suggest', ($, e, next) =>
    pending !== undefined && e.origin.kind === 'suggestion'
      ? next({ ...e, text: pending })
      : next(e),
  )
}
