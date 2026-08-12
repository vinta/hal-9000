# Claude Code Session Auto-rename

Automatically name each session after what its first prompt is about.

Claude Code already titles each session -- once, from its first real prompt -- and stores it in the transcript as an internal `ai-title` entry. This plugin turns it into a real session name, by reading it from the transcript and emitting it as `sessionTitle` from a `UserPromptSubmit` hook.

## Installation

```bash
claude plugin marketplace add vinta/hal-9000
claude plugin install hal-session-auto-rename@hal-9000
```

Then restart Claude Code.

## Usage

Just use Claude Code as usual -- the session name appears on your second non-queued prompt.

A prompt typed while Claude is still working is queued, and queued prompts never fire `UserPromptSubmit`, so they do not count.

## After `/clear`: a fresh name instead of a stale copy

`/clear` starts a new session that inherits the old session's name, and Claude Code never generates an `ai-title` for a session that starts out named -- so both sessions would sit in `/resume` under the same name forever. When the inherited name is one this plugin created, the new session gets a freshly generated name instead: on your first prompt after `/clear` a background worker summarizes the new conversation (with `claude --model haiku`, or a local Ollama model when `HAL_SESSION_AUTO_RENAME_USE_OLLAMA=1`), and your next prompt applies it. Until that lands, the inherited name stays.

The plugin tracks the names it set in per-session files under `$TMPDIR/hal-session-auto-rename/`. A name it cannot trace to itself -- `--name`, `/rename`, or a name inherited from before this state existed -- is never touched, and renaming a session yourself permanently stops the plugin from naming that session.

## Sessions this plugin cannot name

A session launched named (`--name`) keeps its name for life: Claude Code generates no `ai-title` for it, and this plugin treats the name as yours.
