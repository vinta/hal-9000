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

## Sessions this plugin cannot name

A session that already has a name when it starts -- launched with `--name`, or carrying the previous session's name through `/clear` -- never gets an `ai-title` generated for it, for its whole life. There is nothing in its transcript for this plugin to read, so its name stays whatever it started as. After `/clear` that means the old and the new session sit in `/resume` under the same name; use `/rename` to tell them apart.
