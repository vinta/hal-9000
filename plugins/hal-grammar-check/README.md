# Claude Code Grammar Check

A grammar check on your prompt while you type, with explanations in Traditional Chinese. The corrections show up above the prompt box, before you hit Enter.

## Installation

With the default `ollama/gemma4:31b-mlx` model, **this plugin needs a local [Ollama](https://ollama.com/)** with that model pulled:

```bash
ollama pull gemma4:31b-mlx
```

It's a [mod](https://code.claude.com/docs/en/plugins/mods/overview), so it also needs Claude Code 2.1.287 or later.

```bash
claude plugin install hal-grammar-check --marketplace vinta/hal-9000
```

Then restart Claude Code.

## Usage

Just type. About 250ms after you stop, the draft goes to the model and the result shows up above the prompt box. A result for an older draft is dropped.

[hal-statusline](../hal-statusline) checks each prompt after you submit it. To avoid seeing both, turn that one off with `HAL_STATUSLINE_GRAMMAR_CHECK_DISABLED=1` in your environment variables.

## Options

- `model`: which model checks your draft, default `ollama/gemma4:31b-mlx`.
  - `ollama/<model>` runs on your local Ollama at `localhost:11434`.
  - `claude/<alias or id>` (e.g. `claude/haiku`) runs on your Claude account. It bills one call every time you pause typing, so it's the costlier choice.

## Privacy

It sends the first 500 characters of your draft to the model. With `ollama/…`, that's your local Ollama at `localhost:11434`: fully offline, nothing leaves your machine. With `claude/…`, it goes to Anthropic through your Claude account, like any other prompt.

## Screenshots

![Claude Code Grammar Check example](https://raw.githubusercontent.com/vinta/hal-9000/main/assets/claude-code-grammar-check.png)
