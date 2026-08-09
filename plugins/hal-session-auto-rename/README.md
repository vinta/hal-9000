# hal-session-auto-rename

Names every Claude Code session automatically, so the prompt bar shows `refactor-auth-middleware` instead of nothing, and `/resume` and the terminal title show the same short name.

Claude Code already summarizes each session with a title of its own, stored in the transcript as `{"type":"ai-title","aiTitle":"Refactor auth middleware"}`, but that title only reaches the `/resume` picker. This plugin turns it into a real session name -- the same thing `--name` and `/rename` set -- by reading it from the transcript and emitting it as `sessionTitle` from a `UserPromptSubmit` hook.

## How it works

Claude Code writes the first `ai-title` after the first assistant turn, so a brand-new session has nothing to read yet. The naming therefore lands on your second prompt:

1. You send the first prompt. The hook finds no `ai-title` and exits silently.
2. Claude answers, and Claude Code writes its `ai-title`.
3. You send the second prompt. The hook reads the newest `ai-title`, converts `Refactor auth middleware` to `refactor-auth-middleware` (lowercase, hyphenated, cut to 30 terminal columns at a word boundary), and the session is renamed.

The hook only reads a file, so it adds no measurable latency to the prompt and never calls a model.

Claude Code keeps updating `ai-title` as the conversation drifts, and the session name follows it: the hook sees the session's current name in the `session_title` field of its input, and when the newest `ai-title` slugs to something different, the session is renamed again.

A name you set yourself with `claude --name` or `/rename` sticks. Every name this hook applies is the slug of some recent `ai-title`, so when the current name matches none of them, the hook knows the name is yours and backs off.

## Installation

```bash
claude plugin marketplace add vinta/hal-9000
claude plugin install hal-session-auto-rename@hal-9000
```

Then restart Claude Code.

## Limitations

- The name arrives one turn late, and its wording comes from Claude Code's summary rather than from your own prompt.
- A session that ends after a single prompt is never named.
- If you manually name the session the exact slug of a recent `ai-title`, the hook mistakes the name for one of its own and may still rename it later.

## Debugging

The hook logs every decision to `/tmp/hal-session-auto-rename.log`.
