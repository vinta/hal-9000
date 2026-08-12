# Claude Code Session Auto-rename

Automatically name each session, and optionally re-name it as the conversation drifts.

Claude Code already titles each session -- once, from its first real prompt -- and stores it in the transcript as an internal `ai-title` entry. This plugin turns it into a real session name, by reading it from the transcript and emitting it as `sessionTitle` from a `UserPromptSubmit` hook.

## Installation

```bash
claude plugin marketplace add vinta/hal-9000
claude plugin install hal-session-auto-rename@hal-9000
```

Then restart Claude Code.

## Usage

Just use Claude Code as usual -- the session name appears on your second (**non-queued**) prompt.

A prompt typed while Claude is still working is queued, and queued prompts never fire `UserPromptSubmit`, so they do not count.

## Environment Variables

- `HAL_SESSION_AUTO_RENAME_REFRESH_EVERY_N_PROMPTS=5`: any value > `0` enables the refresh mode.
- `HAL_SESSION_AUTO_RENAME_USE_OLLAMA=1`: `1` uses local Ollama model for auto-renaming; Otherwise, `claude --model haiku -p`.

### User-named Session

A session launched named (`--name`) or `/rename` in mid-session keeps its name for life: Claude Code generates no `ai-title` for it, and this plugin treats the name as yours and WILL NOT auto-rename. Unless refresh mode is enabled.

### Refresh mode

By default, the session title only set once per session. If you want the plugin to rename the session title as the conversation drifts. Set `HAL_SESSION_AUTO_RENAME_REFRESH_EVERY_N_PROMPTS=5` (any N > 0; unset or 0 disables) and every N prompts the plugin regenerates the name from the recent conversation with a background worker, applied on your next prompt.

The refresh overrides whatever name the session currently has -- one this plugin set, one carried through `/clear`, or one you set yourself with `--name` or `/rename`.
