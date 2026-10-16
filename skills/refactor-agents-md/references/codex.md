# Codex

## Which files load

- User-level: `$CODEX_HOME/AGENTS.override.md` if present, else `$CODEX_HOME/AGENTS.md`, with `~/.codex` as the default Codex home.
- Project: from the project root down to the working directory, each directory contributes one file, the first of `AGENTS.override.md`, `AGENTS.md`, and the names in `project_doc_fallback_filenames`. Files closer to the working directory come later and override earlier ones.
- Loading stops once the combined size reaches `project_doc_max_bytes`, 32 KiB by default.
- `CLAUDE.md` loads only when `project_doc_fallback_filenames` lists it.

## Guides

Reuse current guidance already fetched in the conversation; fetch missing sections needed for the audit. If a source is unavailable, disclose the gap and continue with available evidence.

- For GPT behavior: https://developers.openai.com/api/docs/guides/latest-model. Always target the most capable GPT model identified by the current official guide and read its prompting best practices.
- For refactoring criteria: find and fetch current official OpenAI guidance on refactoring skills and prompts for that model.
- When moving guidance between files or resolving loading and precedence: https://learn.chatgpt.com/docs/agent-configuration/agents-md

## Demote destinations

- The nearest nested `AGENTS.md` whose whole subtree shares the guidance. It loads only when the session starts inside that directory, so for a rule that must reach Codex sessions started at the repo root, use the next option.
- A linked doc, with a pointer naming the tasks that need it.
- A skill with a reliable trigger.
