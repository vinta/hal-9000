# Claude Code Statusline with English Grammar Check

A custom [Claude Code statusline](https://code.claude.com/docs/en/statusline) that shows the current model, directory, and git branch -- plus **a grammar check on every prompt you type**, with corrections explained in Traditional Chinese.

## Installation

```bash
curl -sL https://raw.githubusercontent.com/vinta/hal-9000/main/scripts/install-hal-statusline.sh | bash
```

Then restart Claude Code.

## Configurations

Set `HAL_STATUSLINE_GRAMMAR_CHECK_USE_OLLAMA=1` in your environment to use a local Ollama model instead of `claude -p`.

## Screenshots

![Claude Code Statusline with English Grammar Check example](https://raw.githubusercontent.com/vinta/hal-9000/main/assets/claude-code-statusline-grammar-check.png)
