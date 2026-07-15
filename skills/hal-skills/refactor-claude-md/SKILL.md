---
name: refactor-claude-md
description: Use when you want to refactor a CLAUDE.md, user-level or project-level, for progressive disclosure
argument-hint: [user | project]
user-invocable: true
disable-model-invocation: true
allowed-tools:
  - AskUserQuestion
  - WebFetch
  - Read(~/.claude/CLAUDE.md)
  - Edit(~/.claude/CLAUDE.md)
  - Edit(CLAUDE.md)
  - Write(~/.claude/rules/**)
  - Write(.claude/rules/**)
---

# Overview

Refactor a CLAUDE.md toward progressive disclosure. Every line it keeps is loaded into every session the file covers, and a frontier model follows only around 150 to 200 standing instructions consistently, so each line competes for that budget. Everything else moves down the ladder or out of the file.

## Instructions

1. **Pick the target.** If the invocation names one, use it. Otherwise ask with `AskUserQuestion`, one option per file that exists, with the resolved path in the label:
   - The user-level CLAUDE.md at `~/.claude/CLAUDE.md`
   - The current project's CLAUDE.md

2. **Fetch the yardsticks.** Fetch these pages. They calibrate the delete and rewrite verdicts below:
   - https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
   - https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5

3. **Audit.** Read the file and give every instruction exactly one verdict, judged against the target's bar below. Done when no instruction lacks one.
   - **contradiction**: conflicts with another instruction. Record both sides.
   - **delete**: fails the no-op test, meaning the agent would behave the same without it. Covers instructions the agent already follows by default, instructions too vague to act on, and platitudes like "write clean code".
   - **demote**: real instruction that only applies to some paths or tasks. Pick its destination from the bar. If it describes a multi-step workflow, propose a skill instead. Name the destination in the sign-off.
   - **rewrite**: right meaning, phrasing falls short of the fetched best practices.
   - **keep**: earns its always-loaded cost as written.

   The bar per target:
   - **User-level** (loaded into every session in every project): a keep must apply across all projects. Demote destination: a `paths:`-scoped file in `~/.claude/rules/`.
   - **Project-level** (loaded into every session in this project): a keep must be underivable from the code: a one-sentence project description, commands the agent would guess wrong, domain concepts, gotchas. Lines restating what the code already shows, and volatile detail like file trees, are deletes because they go stale and stale lines poison the context. Demote destinations: a `paths:`-scoped file in `.claude/rules/`, or a doc file linked from CLAUDE.md.

4. **Get decisions.** One `AskUserQuestion` per contradiction, with each conflicting version as an option. Then present the delete and demote lists for sign-off. The file stays untouched until sign-off.

5. **Rewrite.** Apply the signed-off verdicts in one pass. When creating a new rules file, fetch https://code.claude.com/docs/en/memory#path-specific-rules for the `paths:` frontmatter syntax. Done when every audited instruction landed where its verdict says: kept, rewritten, demoted, or deleted.
