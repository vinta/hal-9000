# Claude Code Grammar Check

A grammar check on your prompt while you type, with explanations in Traditional Chinese. The corrections show up above the prompt box, before you hit Enter.

## Installation

```bash
claude plugin install hal-grammar-check --marketplace vinta/hal-9000
```

Then restart Claude Code.

## Usage

Just type.

The grammar-check result of your prompt shows up above the prompt box after you stop typing.

[hal-statusline](../hal-statusline) also checks each prompt after you submit it. If you use both, turn that one off with `HAL_STATUSLINE_GRAMMAR_CHECK_DISABLED=1` in your environment variables.

## Options

Set them in `/config`:

- `model`: which of the two models below checks your draft, default `claude/haiku`.
  - `claude/haiku` runs on your Claude account. It bills one call every time you pause typing.
  - `ollama/gemma4:26b-nvfp4` runs on your local Ollama at `localhost:11434`. It's the free, offline choice.

Pick `ollama/gemma4:26b-nvfp4` to keep everything on your machine. That needs a local [Ollama](https://ollama.com/) with the model pulled:

```bash
ollama pull gemma4:26b-nvfp4
```

## Privacy

It sends the first 500 characters of your draft to the model. With `claude/haiku`, it goes to Anthropic through your Claude account, like any other prompt. With an `ollama/` model, that's your local Ollama at `localhost:11434`: fully offline, nothing leaves your machine.

## Screenshots

![Claude Code Grammar Check example](https://raw.githubusercontent.com/vinta/hal-9000/main/assets/claude-code-grammar-check.png)
