---
name: refactor-agents-md
description: Use when about to refactor or refine a user-level or project-level AGENTS.md
allowed-tools:
  - WebFetch
  - Read(~/.codex/AGENTS.md)
---

# Refactor AGENTS.md

Refactor an `AGENTS.md` for GPT-6 Astra. Every retained line enters each Codex session in its scope, so it must earn that attention. Move narrower guidance to the closest applicable scope or a reusable skill, and remove instructions that do not change behavior. Preserve the user's intended behavior and existing authorization.

## Instructions

Use `request_user_input` in Codex when available.

1. **Pick the target.** Use the target named by the invocation or established in the conversation. If the target remains ambiguous, ask the user to choose among the files that exist:
   - The user-level file at `$CODEX_HOME/AGENTS.md`, defaulting to `~/.codex/AGENTS.md` when `CODEX_HOME` is unset.
   - The current project's root `AGENTS.md`.
   - Any nested `AGENTS.md` on the path from the project root to the current working directory.

2. **Consult relevant guidance.** Reuse current guidance already fetched in the conversation; fetch missing sections needed for the audit. Preserve explicit user choices where the guides offer defaults. If a source is unavailable, disclose the gap and continue with available evidence.
   - For refactoring criteria: https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra
   - For GPT-6 Astra behavior: https://developers.openai.com/api/docs/guides/latest-model?model=gpt-6-astra#prompting-best-practices
   - When moving guidance between files or resolving loading and precedence: https://learn.chatgpt.com/docs/agent-configuration/agents-md

3. **Audit.** Match the audit to the request. Read the target and applicable broader `AGENTS.md` files, then follow references needed to assess scope, conflicts, or claimed redundancy. Treat referenced workflows as audit material. For a full audit or refactor, cover every instruction; for a targeted edit, cover the affected instructions and their interactions. Check repository evidence before declaring a rule stale or derivable. Finish when every instruction in scope has exactly one verdict against the target's bar and GPT-6 checks below.
   - **contradiction**: conflicts with another applicable instruction. Record both instructions and their source files; resolve conflicts from instruction priority and explicit user intent where possible.
   - **delete**: fails the no-op test because GPT-6 Astra would behave the same without it. This includes redundant defaults, vague directions, and platitudes such as "write clean code." Cite the evidence or rationale; retain an explicit constraint when its redundancy is uncertain.
   - **demote**: changes behavior but applies only to a narrower directory or task. Choose and name its destination. Put directory-specific guidance in the closest nested `AGENTS.md`; put a multi-step task workflow in a skill; put reference material in a linked document.
   - **rewrite**: has the right scope and meaning, but its phrasing falls short of the fetched prompting guidance. Also a rewrite when the line carries words that fail the no-op test on their own: a duplicate of another line, a definition of a term the model knows, or emphasis; a rationale or example stays, since both steer the model.
   - **keep**: earns its always-loaded cost as written.

   Apply the bar for the target:
   - **User-level**: a keep must express a preference or constraint across projects. Conditional tool and environment rules qualify when their trigger can recur across projects. Demote project or directory guidance to the applicable project's `AGENTS.md`, and detailed task workflows to skills with reliable triggers.
   - **Project or nested**: a keep must govern the target directory's subtree; conditional rules belong here when their trigger can occur throughout that scope. Keep concise project context, commands Codex would otherwise guess wrong, domain concepts, constraints, and gotchas that are not obvious from the repository. Delete restatements of the code and volatile inventories such as file trees. Demote narrower guidance to a closer nested `AGENTS.md`, a linked document, or a skill.

4. **Prepare decisions.** Prepare the proposed rewrite and the delete and demote lists, including every destination. Use `request_user_input` when available and permitted to resolve contradictions and let the user select which proposed changes to apply; otherwise ask one concise question. Leave files untouched until those specific changes are approved. A general request to refactor authorizes preparing the proposal, not applying it. Continue independent audit and draft work while decisions are pending. Newly discovered changes remain proposals until approved.

5. **Rewrite and verify.** Apply only the changes the user selected and approved. Search references before removing or moving guidance, and update affected pointers. Place each new nested `AGENTS.md` in the nearest directory whose whole subtree shares its guidance. Check the final diff for preserved intent, resolved conflicts, and reachable destinations. Finish when every audited instruction is accounted for and required checks pass; report changed files and any unresolved decisions concisely.

## GPT-6 checks

Apply these checks to existing instructions; add guidance only where the user's workflow needs it.

- **Initiative:** Replace unnecessary approval gates with clear authority and stopping conditions. Complete authorized work, use context for routine choices, and prepare a reviewable result before any required approval. Preserve deliberate approval boundaries.
- **Instruction priority:** Make explicit that user instructions take precedence over skill guidelines within higher-priority constraints. Audit vague rules that could silently stop or redirect work. When a skill causes a pause or deviation, require its exact path, relevant quote, and explanation distinguishing the rule from the agent's interpretation.
- **Writing:** State the desired length and structure directly. Prefer concise prose and useful technical detail; reserve lists and tables for information they clarify. Remove overlapping style rules and stock phrasing prescriptions that add no value.
- **Delegation:** State when subagents help and any limits when the workflow uses them. Preserve tool availability and explicit delegation preferences; the guide's example is not a blanket requirement to delegate every task.
- **Verification:** Match checks to the change and complete mandatory checks. Broaden or repeat testing only for new changes, failures, or unresolved concerns. Avoid requiring new tests that merely restate low-impact edits.
