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

Just type. About 400ms after you stop, the draft goes to Ollama and the result shows up above the prompt box. A result for an older draft is dropped.

It checks the words after a slash command (`/pr merge it`), skips bash mode (`!`), and dims the band when you submit.

If Ollama is not running, the band shows `ollama unreachable (...)`.

### With hal-statusline

[hal-statusline](../hal-statusline) checks each prompt after you submit it. To avoid seeing both, turn that one off with `HAL_STATUSLINE_GRAMMAR_CHECK_DISABLED=1`.

## Privacy

It sends the first 500 characters of your draft to your local Ollama at `localhost:11434`. Fully offline, nothing leaves your machine.
