# Codex

## Which files load

- User-level: `$CODEX_HOME/AGENTS.override.md` if present, else `$CODEX_HOME/AGENTS.md`, with `~/.codex` as the default Codex home.
- Project: from the project root down to the working directory, each directory contributes one file, the first of `AGENTS.override.md`, `AGENTS.md`, and the names in `project_doc_fallback_filenames`. Files closer to the working directory come later and override earlier ones.
- Loading stops once the combined size reaches `project_doc_max_bytes`, 32 KiB by default.
- `CLAUDE.md` loads only when `project_doc_fallback_filenames` lists it.

## Guides

Reuse current guidance already fetched in the conversation; fetch missing sections needed for the audit. If a source is unavailable, disclose the gap and continue with available evidence.

- For refactoring criteria: https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra
- For GPT-6 Astra behavior: https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra#prompting-best-practices
- When moving guidance between files or resolving loading and precedence: https://learn.chatgpt.com/docs/agent-configuration/agents-md

## Demote destinations

- The nearest nested `AGENTS.md` whose whole subtree shares the guidance. It loads only when the session starts inside that directory, so for a rule that must reach Codex sessions started at the repo root, use the next option.
- A linked doc, with a pointer naming the tasks that need it.
- A skill with a reliable trigger.

## GPT-6 checks

Apply these checks to existing instructions; add guidance only where the user's workflow needs it.

- **Reading scope:** Replace unconditional document-reading requirements with pointers naming the tasks that need each document. Keep exhaustive reading for audits that require full coverage.
- **Initiative:** Replace unnecessary approval gates with clear authority and stopping conditions. Complete authorized work, use context for routine choices, and prepare a reviewable result before any required approval. Preserve deliberate approval boundaries.
- **Instruction priority:** Make explicit that user instructions take precedence over skill guidelines within higher-priority constraints. Audit vague rules that could silently stop or redirect work. When a skill causes a pause or deviation, require its exact path, relevant quote, and explanation distinguishing the rule from the agent's interpretation.
- **Writing:** State the desired length and structure directly. Prefer concise prose and useful technical detail; reserve lists and tables for information they clarify. Remove overlapping style rules and stock phrasing prescriptions that add no value.
- **Delegation:** State when subagents help and any limits when the workflow uses them. Preserve tool availability and explicit delegation preferences; the guide's example is not a blanket requirement to delegate every task.
- **Verification:** Match checks to the change and complete mandatory checks. Broaden or repeat testing only for new changes, failures, or unresolved concerns. Avoid requiring new tests that merely restate low-impact edits.
