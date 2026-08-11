# Claude Code Session Auto-rename

Automatically name each session and rename it as the conversation evolves.

Claude Code already summarizes each session with a title, stored in the transcript as an internal `ai-title` entry. This plugin turns it into a real session name -- by reading it from the transcript and emitting it as `sessionTitle` from a `UserPromptSubmit` hook.

## Installation

```bash
claude plugin marketplace add vinta/hal-9000
claude plugin install hal-session-auto-rename@hal-9000
```

Then restart Claude Code.

## Usage

Just use Claude Code as usual -- the session name appears on your second non-queued prompt, then changes as the conversation evolves.

A prompt typed while Claude is still working is queued, and queued prompts never fire `UserPromptSubmit`, so they do not count.

`/clear` carries the current name into the new session, and Claude Code never generates titles for a session whose name arrived through `/clear` or `--name` -- so without help, the old and new sessions would sit in `/resume` under the same name forever. When the inherited name is one this plugin set (the slug of some session's internal title) and it exactly duplicates another recent session's name, the new session gets a `-2` suffix (`-3` on the next `/clear`, and so on). Names you set yourself with `--name` or `/rename` are never touched.
