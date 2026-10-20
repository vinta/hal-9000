# Claude Code Session Auto-rename

Automatically name each session and rename it as the conversation evolves.

After your first turn (your prompt plus everything Claude does until it stops), and every N turns after that, the model you pick (haiku by default) writes a short title from how the session started and the recent conversation. The plugin applies it with `/rename`, so every change shows up as a `/rename` row in the transcript.

## Installation

```bash
claude plugin install hal-session-auto-rename --marketplace vinta/hal-9000
```

Then restart Claude Code.

## Usage

Just use Claude Code as usual. By default N is 5. A new title that shares at least half its words with the current one, counted against the longer of the two, is only a rewording, so it's skipped. Each `/rename` makes Claude Code tell the model that the user named the session. That's not true for this plugin's renames, so the plugin rewrites that system reminder to say the title was auto-generated.

If you name the session yourself, with `/rename` or `--name`, the plugin never touches it again.

In the Claude desktop app, the plugin does nothing. The app shows its own session title, so a rename there changes nothing you can see, and its `/rename` row would dismiss the app's next-step box.

## Options

Set them in `/config`:

- `model`: which of the two models below writes the title, `claude/haiku` by default.
  - `claude/haiku` runs on your Claude account. It bills one call for every title.
  - `ollama/gemma4:26b-nvfp4` runs on your local [Ollama](https://ollama.com/) at `localhost:11434`. It's the free, offline choice.
- `refreshEveryNTurns`: how often to regenerate the title, `5` by default. `0` keeps the first title.

Pick `ollama/gemma4:26b-nvfp4` to keep everything on your machine. That needs a local [Ollama](https://ollama.com/) with the model pulled:

```bash
ollama pull gemma4:26b-nvfp4
```

## Privacy

It sends the current title and the first 1500 and last 2000 characters of your conversation to the model you pick. With `claude/haiku`, it goes to haiku through the session's own API client, on your Claude account. With an `ollama/` model, it goes to `localhost:11434` instead, and nothing leaves your machine.

The plugin's store holds one entry per session: a flag for a session you named yourself, otherwise the last title the plugin set, so a resume can tell the two apart.
