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
