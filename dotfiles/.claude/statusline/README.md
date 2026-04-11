# Claude Code Statusline with English Grammar Check

Show the current model, directory, and git branch in [statusline](https://code.claude.com/docs/en/statusline). Plus **a grammar check on every prompt you type**, with explanations in Traditional Chinese.

## Installation

```bash
curl -L https://raw.githubusercontent.com/vinta/hal-9000/main/scripts/install-hal-statusline.sh | bash
```

Set `HAL_STATUSLINE_GRAMMAR_CHECK_USE_OLLAMA=1` in your environment to use a local Ollama model instead of `claude -p`.

## Screenshots

![Claude Code Statusline with English Grammar Check example](https://raw.githubusercontent.com/vinta/hal-9000/main/assets/claude-code-statusline-grammar-check.png)
