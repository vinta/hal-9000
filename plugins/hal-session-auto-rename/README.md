# Claude Code Session Auto-rename

Names every Claude Code session automatically.

Claude Code already summarizes each session with a title through an internale tool named `ai-title`. This plugin turns it into a real session name -- by reading it from the transcript and emitting it as `sessionTitle` from a `UserPromptSubmit` hook.

## Installation

```bash
claude plugin marketplace add vinta/hal-9000
claude plugin install hal-session-auto-rename@hal-9000
```

Then restart Claude Code.

## Usage

Just use Claude Code as usual -- you will see the session name arrives one turn late after your prompts
