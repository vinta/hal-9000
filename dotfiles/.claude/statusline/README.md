# Claude Code Statusline with English Grammar Check

A custom [Claude Code statusline](https://code.claude.com/docs/en/statusline) that shows the current model, directory, and git branch -- plus **a grammar check on every prompt you type**, with corrections explained in Traditional Chinese.

## Setup

In `~/.claude/settings.json`:

```json
{
  "statusline": {
    "script": "~/.claude/statusline/run.py"
  }
}
```

## Screenshots

![Grammar check example 1](https://raw.githubusercontent.com/vinta/hal-9000/master/assets/claude-code-statusline-grammar-check-1.jpeg)

![Grammar check example 2](https://raw.githubusercontent.com/vinta/hal-9000/master/assets/claude-code-statusline-grammar-check-2.jpeg)
