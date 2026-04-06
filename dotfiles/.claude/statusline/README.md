# Claude Code Statusline with English Grammar Check

A custom [Claude Code statusline](https://code.claude.com/docs/en/statusline) that shows the current model, directory, and git branch -- plus **a grammar check on every prompt you type**, with corrections explained in Traditional Chinese.

## Setup

Download the script:

```bash
curl -fsSL https://raw.githubusercontent.com/vinta/hal-9000/main/dotfiles/.claude/statusline/run.py \
  -o ~/.claude/statusline/run.py \
  --create-dirs
```

Add to `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "python3 ~/.claude/statusline/run.py"
  }
}
```

Add `STATUSLINE_GRAMMAR_CHECK_USE_OLLAMA=1` to your environment variables if you want to use `ollama run` for a local model instead.

## Screenshots

![Claude Code Statusline with English Grammar Check example](https://raw.githubusercontent.com/vinta/hal-9000/main/assets/claude-code-statusline-grammar-check.png)
