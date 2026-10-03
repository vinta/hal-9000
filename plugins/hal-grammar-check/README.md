# Claude Code Grammar Check

<img src="icon.svg" width="128" alt="vinta/hal-9000 icon">

A grammar check on your prompt while you type, with explanations in Traditional Chinese. The corrections show up above the prompt box, before you hit Enter.

## Installation

**This plugin needs a local [Ollama](https://ollama.com/)** with the `gemma4:31b-mlx` model:

```bash
ollama pull gemma4:31b-mlx
```

It's a [mod](https://code.claude.com/docs/en/plugins/mods/overview), so it also needs Claude Code 2.1.287 or later.

```bash
claude plugin marketplace add vinta/hal-9000
claude plugin install hal-grammar-check@hal-9000
```

Then restart Claude Code.

## Usage

Just type. About 250ms after you stop, the draft goes to Ollama and the result shows up above the prompt box. A result for an older draft is dropped.

[hal-statusline](../hal-statusline) checks each prompt after you submit it. To avoid seeing both, turn that one off with `HAL_STATUSLINE_GRAMMAR_CHECK_DISABLED=1` in your environment variables.

## Privacy

It sends the first 500 characters of your draft to your local Ollama at `localhost:11434`. Fully offline, nothing leaves your machine.

## Screenshots

![Claude Code Grammar Check example](https://raw.githubusercontent.com/vinta/hal-9000/main/assets/claude-code-grammar-check.png)
