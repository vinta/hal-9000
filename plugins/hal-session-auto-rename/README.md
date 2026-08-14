# Claude Code Session Auto-rename

Automatically name each session, and optionally rename it as the conversation evolves.

Claude Code already titles each session once, from its first real prompt, and stores that title in the transcript as an internal `ai-title` entry. This plugin turns it into a real session title: a `UserPromptSubmit` hook reads the entry and emits it as `sessionTitle`.

## Installation

```bash
claude plugin marketplace add vinta/hal-9000
claude plugin install hal-session-auto-rename@hal-9000
```

Then restart Claude Code.

## Usage

Just use Claude Code as usual. The session title appears on your **second** prompt, as long as that prompt is not queued (queued prompts never fire `UserPromptSubmit`, so they cannot set the title) and your first prompt was not a slash command.

## Environment Variables

- `HAL_SESSION_AUTO_RENAME_REFRESH_EVERY_N_PROMPTS=5`: any value above `0` enables refresh mode.
- `HAL_SESSION_AUTO_RENAME_USE_OLLAMA=1`: generate the session title with a local Ollama model instead of `claude --model haiku -p`.

### User-named Session

A session you named keeps that title for life, whether you passed `--name` at launch or ran `/rename` mid-session. Claude Code generates no `ai-title` for it, so this plugin treats the session title as yours and WILL NOT auto-rename it. Refresh mode is the only exception.

### Refresh Mode

By default the session title is set once per session. If you want the plugin to rename the session as the conversation evolves, turn on refresh mode by setting `HAL_SESSION_AUTO_RENAME_REFRESH_EVERY_N_PROMPTS=5` (any N > `0`): every N prompts, a background worker regenerates the session title from the recent conversation, applied on your next prompt; unset or `0` disables it.

The refresh overrides whatever name the session currently has: one this plugin set, one carried through `/clear`, or one you set with `--name` or `/rename`.
