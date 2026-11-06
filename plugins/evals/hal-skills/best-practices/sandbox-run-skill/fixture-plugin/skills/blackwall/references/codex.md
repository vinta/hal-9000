# Under `blackwall codex`

- The config folder is `~/.codex-blackwall`.
- `AGENTS.md` and `agents` are copied from `~/.codex`, and skills from `~/.agents/skills`, on every launch, so edits to the copies vanish. Make user-level instruction edits outside the sandbox, in `~/.codex`, and skill edits in `~/.agents/skills`; files in the current folder persist.
- Command rules stay separate in `~/.codex-blackwall/rules/`; launches preserve them.
- Login is separate: run `blackwall codex login --device-auth`.
- Commits are unsigned: `commit.gpgsign=false` is injected because gpg can't reach `~/.gnupg`.
- Temporary files use `$TMPDIR` (`/tmp/claude`, the sandbox runtime's shared temp directory); the rest of `/tmp` is write-denied.
- Codex's own sandbox is off inside; blackwall is the sandbox.
