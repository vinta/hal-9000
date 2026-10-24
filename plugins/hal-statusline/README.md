# Claude Code Statusline with English Grammar Check

A custom [Claude Code statusline](https://code.claude.com/docs/en/statusline) that shows the current model and effort level, directory, git branch, context usage, and your 5h/7d rate limit usage. Plus **a grammar check on every prompt you type**, with corrections explained in Traditional Chinese.

The statusline also shows a row for each running subagent: its name, type, model, effort, and context usage.

## Installation

```bash
curl -sL https://raw.githubusercontent.com/vinta/hal-9000/main/scripts/install-hal-statusline.sh | bash
```

Then restart Claude Code.

## Usage

Just use Claude Code as usual. The statusline appears below the input box.

## Environment Variables

- `HAL_STATUSLINE_GRAMMAR_CHECK_DISABLED=1`: turn off the grammar check and show only the basic info line.
- `HAL_STATUSLINE_GRAMMAR_CHECK_MODEL=<backend>/<model>`: pick the grammar check model, either `claude/<alias or id>` for `claude --model <name> -p` or `ollama/<model>` for a local Ollama model, defaulting to `claude/haiku`.

## Screenshots

![Claude Code Statusline with English Grammar Check example](https://raw.githubusercontent.com/vinta/hal-9000/main/assets/claude-code-statusline-grammar-check.png)

![Claude Code Statusline subagent rows example](https://raw.githubusercontent.com/vinta/hal-9000/main/assets/claude-code-statusline-subagents.png)
