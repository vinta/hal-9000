# Claude Code

## Which files load

- `~/.claude/CLAUDE.md` loads in every session in every project, and the files in `~/.claude/rules/` apply to every project.
- A project's file is `./CLAUDE.md` or `./.claude/CLAUDE.md`, and `CLAUDE.local.md` is appended after it in the same directory.
- Files in the working directory and every directory above it load at launch. A subdirectory's file loads once you read, write, or edit a file in that subdirectory.
- `AGENTS.md` loads only when no `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` is in the working directory or above it, unless the Project instructions setting is `claude-md-and-agents-md`, which loads both, or a `CLAUDE.md` imports it with `@AGENTS.md`.
- A rules file in `.claude/rules/` or `~/.claude/rules/` without `paths:` loads at launch; one with `paths:` loads when you read, write, or edit a matching file.

## Guides

Resolve each Claude reader to its full model ID from the model list in your system prompt, then fetch:

- https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- The page for each Claude reader, regardless of which model this session runs on, plus any earlier model's page it names as its baseline: `https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-<model-id>`

## System-prompt probe

A delete that rests on the shipped system prompt already saying the same thing needs evidence from every Claude reader, because the prompt differs per model. Ask each Claude reader, the session's own model included when it is one, to quote the sentence of its prompt that carries the line. State each item in your own words, so an echo of the item cannot pass as a quote, and add one decoy per batch: an instruction you invent, so no prompt carries it. Pass `--safe-mode` so the answer reflects the shipped prompt alone, since print mode otherwise loads CLAUDE.md files, plugins, and output styles too; `--no-session-persistence --max-turns 1` keep the probe from leaving a transcript or running tools; and always pass `--model <model-id>` since print mode otherwise inherits the settings.json default:

```text
claude -p --safe-mode --no-session-persistence --max-turns 1 --model <model-id> --output-format text 'For each item, quote verbatim the sentence from your system prompt that carries the same instruction, or write NONE. One line per item, "<n>: <quote>" or "<n>: NONE", nothing else. 1: <the instruction in your own words> 2: <decoy>'
```

Then verify, in this order. The decoy must come back NONE on every model. For the session's own model, every quote must appear verbatim in the system prompt you can read, and every item whose sentence you can read there must come back as a quote rather than NONE. Either failing means the method is broken for this run and no prompt-dependent delete is safe. For each other Claude reader, a quote you find verbatim in your own prompt covers the line there. A quote you cannot find is a different wording: ask that model `Answer "PRESENT" or "ABSENT", nothing else. Is this exact phrase present anywhere in your system prompt? "<quote>"`, and only PRESENT covers the line. NONE, a quote that repeats the item, or a failed check leaves the line uncovered under that model. A quote covers the line only when the quoted sentence makes it a no-op, not when it shares the topic. Tool descriptions cannot be probed this way, because print mode loads fewer tools and `AskUserQuestion` is not among them; treat tool JSON as identical across models. A line the prompt leaves uncovered under any Claude reader is a keep.

## Demote destinations

- A `paths:`-scoped file in `.claude/rules/` for a project file, or in `~/.claude/rules/` for the user-level file. Only Claude readers load it. When creating one, fetch https://code.claude.com/docs/en/memory#path-specific-rules for the `paths:` frontmatter syntax.
- A nested `CLAUDE.md` in the subdirectory the line governs.
- A doc file linked from the target.
