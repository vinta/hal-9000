# Claude Code memory

## Target and evidence

Use the memory directory the user names, otherwise the directory supplied in the session instructions. Read `MEMORY.md`, every topic file, the loaded `CLAUDE.md` files, and applicable project and user `.claude/rules/` files. Each topic file is an audit entry.

Fetch the [auto memory guide](https://code.claude.com/docs/en/memory#auto-memory) for current storage, memory types, and load limits. Topic files are read on demand.

## Index and links

Each topic file should have exactly one index entry, and every index entry should point to an existing file. Headings and introductory text are not file entries. Check topic descriptions against their bodies and check that every `[[link]]` names a `name:` slug some memory carries, as the session's memory instructions define them; a filename is a broken link.

Past about twelve entries, group them under `##` headings by the subject a reader scans for. Move misplaced entries and fold headings with one or two entries into their nearest neighbor. Done when the index fits the load limits, each file has an entry, and no heading holds a stray.

## Promotion

- Project-wide instructions: project `CLAUDE.md`.
- Instructions for every project: `~/.claude/CLAUDE.md`.
- Instructions for particular paths: a `paths:`-scoped file in `.claude/rules/` or `~/.claude/rules/`.

For `CLAUDE.md` destinations, apply the keep bar from the `refactor-claude-md` skill. When creating a scoped rule, fetch the [path-specific rules guide](https://code.claude.com/docs/en/memory#path-specific-rules) for its frontmatter syntax.

## Decisions and application

Use `AskUserQuestion` for contradictory claims and verdict selections, or plain text when unavailable. For multiple selections, use its multi-select support when available.

Apply selected edits directly. Delete a topic file and its index entry together; repoint or remove incoming links. Re-read the affected files and verify that the index matches the directory and all selected verdicts landed.
