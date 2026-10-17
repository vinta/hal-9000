# Claude Code Session Auto-rename

Automatically name each session and rename it as the conversation evolves.

After your first turn, and every N turns after that, haiku (or your local Ollama) writes a short title from the recent conversation. The plugin applies it with `/rename`, so every change shows up as a `/rename` row in the transcript.

## Installation

It's a [mod](https://code.claude.com/docs/en/plugins/mods/overview), so it needs Claude Code 2.1.302 or later.

```bash
claude plugin install hal-session-auto-rename --marketplace vinta/hal-9000
```

Then restart Claude Code.

## Usage

Just use Claude Code as usual. By default N is 5. A title that comes out the same as the current one is skipped.

Name the session yourself, with `/rename` or `--name`, and the plugin never touches it again.

Each `/rename` makes Claude Code tell the model that the user named the session. That's not true for this plugin's renames, so the plugin rewrites that system reminder to say the title was auto-generated.

## Options

Set them in `/config`:

- `refreshEveryNTurns`: how often to regenerate the title, `5` by default. `0` keeps the first title.
- `useOllama`: generate the title with `gemma4:31b-mlx` on your local [Ollama](https://ollama.com/) instead of haiku.

## Privacy

It sends the last 2000 characters of your conversation to haiku, through the session's own API client, on your Claude account. With `useOllama`, it goes to `localhost:11434` instead, and nothing leaves your machine.

The plugin's store holds only one flag per session you named yourself.
