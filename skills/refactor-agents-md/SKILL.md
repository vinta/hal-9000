---
name: refactor-agents-md
description: Use when refactoring a user-level or project-level AGENTS.md for progressive disclosure
user-invocable: true
disable-model-invocation: true
---

# Refactor AGENTS.md

Refactor an `AGENTS.md` toward progressive disclosure. Every retained line enters each Codex session in its scope, so it must earn that attention. Move narrower guidance to the closest applicable scope or a reusable skill, and remove instructions that do not change behavior.

## Instructions

1. **Pick the target.** Use a target named by the invocation. Otherwise ask the user to choose among the files that exist:
   - The user-level file at `$CODEX_HOME/AGENTS.md`, defaulting to `~/.codex/AGENTS.md` when `CODEX_HOME` is unset.
   - The current project's root `AGENTS.md`.
   - Any nested `AGENTS.md` on the path from the project root to the current working directory.

2. **Fetch the yardsticks.** Fetch these pages to calibrate the audit:
   - https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.6
   - https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6
   - https://www.aihero.dev/a-complete-guide-to-agents-md

3. **Audit.** Read the target and applicable broader `AGENTS.md` files. Give every instruction in the target exactly one verdict against the target's bar below. Finish only when every instruction has a verdict.
   - **contradiction**: conflicts with another applicable instruction. Record both instructions and their source files.
   - **delete**: fails the no-op test because Codex would behave the same without it. This includes default behavior, vague directions, and platitudes such as "write clean code."
   - **demote**: changes behavior but applies only to a narrower directory or task. Choose and name its destination. Put directory-specific guidance in the closest nested `AGENTS.md`; put a multi-step task workflow in a skill; put reference material in a linked document.
   - **rewrite**: has the right scope and meaning, but its phrasing falls short of the fetched prompting guidance.
   - **keep**: earns its always-loaded cost as written.

   Apply the bar for the target:
   - **User-level**: a keep must apply across all projects. Demote project or directory guidance to the applicable project's `AGENTS.md`, and task workflows to skills.
   - **Project or nested**: a keep must apply to every task and file in the target directory's subtree and be underivable from the repository. Keep concise project context, commands Codex would otherwise guess wrong, domain concepts, constraints, and gotchas. Delete restatements of the code and volatile inventories such as file trees. Demote narrower guidance to a closer nested `AGENTS.md`, a linked document, or a skill.

4. **Get decisions.** Ask the user to resolve each contradiction. Then present the delete and demote lists, including every proposed destination, for sign-off. Leave all files untouched until the user signs off.

5. **Rewrite.** Apply the signed-off verdicts in one pass. Place each new nested `AGENTS.md` in the nearest directory whose whole subtree shares its guidance. Finish only when every audited instruction is kept, rewritten, demoted to its named destination, or deleted as approved.
