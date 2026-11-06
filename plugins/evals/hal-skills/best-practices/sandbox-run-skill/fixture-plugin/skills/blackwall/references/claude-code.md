# Under `blackwall claude`

- The config folder is `~/.claude-blackwall`.
- `CLAUDE.md`, `rules`, `skills`, `agents`, `commands`, and `output-styles` are copied from `~/.claude` on every launch, so edits to the copies vanish. Make user-level instruction and skill edits outside the sandbox, in `~/.claude`; files in the current folder persist.
- `~/.claude-blackwall/settings.json` stays separate. If missing, it starts with only `enabledPlugins` from the host settings; existing settings are preserved. Host hooks and permissions aren't copied.
- Plugins load from `~/.claude/plugins` read-only, auto-update off. Every launch refreshes `~/.claude-blackwall/plugins/installed_plugins.json` from the host's, so plugin versions follow the host.
- Login is separate: use `/login`, or put `CLAUDE_CODE_OAUTH_TOKEN` in `~/.blackwall/.env`.
- Commits are unsigned: `commit.gpgsign=false` is injected because gpg can't reach `~/.gnupg`.
- Temporary files use `$TMPDIR` (`/tmp/claude`, the sandbox runtime's shared temp directory); the rest of `/tmp` is write-denied.
