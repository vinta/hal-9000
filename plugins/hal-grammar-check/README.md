# Claude Code Grammar Check

A grammar check on your prompt while you type, with explanations in Traditional Chinese. The corrections show up above the prompt box, before you hit Enter.

## Installation

It's a [mod](https://code.claude.com/docs/en/plugins/mods/overview), so it needs Claude Code 2.1.287 or later. The default `claude/haiku` model runs on your Claude account, no setup needed.

```bash
claude plugin install hal-grammar-check --marketplace vinta/hal-9000
```

Then restart Claude Code.

To keep everything on your machine, set `model` to `ollama/<model>` instead. That needs a local [Ollama](https://ollama.com/) with the model pulled:

```bash
ollama pull gemma4:31b-mlx
```

## Usage

Just type. About 250ms after you stop, the draft goes to the model and the result shows up above the prompt box. A result for an older draft is dropped.

[hal-statusline](../hal-statusline) checks each prompt after you submit it. To avoid seeing both, turn that one off with `HAL_STATUSLINE_GRAMMAR_CHECK_DISABLED=1` in your environment variables.

## Options

- `model`: which model checks your draft, default `claude/haiku`.
  - `claude/<alias or id>` runs on your Claude account. It bills one call every time you pause typing.
  - `ollama/<model>` (e.g. `ollama/gemma4:31b-mlx`) runs on your local Ollama at `localhost:11434`. It's the free, offline choice.

## Privacy

It sends the first 500 characters of your draft to the model. With `claude/…`, it goes to Anthropic through your Claude account, like any other prompt. With `ollama/…`, that's your local Ollama at `localhost:11434`: fully offline, nothing leaves your machine.

## Screenshots

![Claude Code Grammar Check example](https://raw.githubusercontent.com/vinta/hal-9000/main/assets/claude-code-grammar-check.png)
