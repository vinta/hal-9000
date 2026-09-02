---
name: refactor-claude-md
description: Use when refactoring a user-level or project-level CLAUDE.md for progressive disclosure
argument-hint: [user | project]
user-invocable: true
allowed-tools:
  - WebFetch
  - Edit(~/.claude/CLAUDE.md)
  - Edit(~/.claude/rules/**)
  - Edit(CLAUDE.md)
  - Edit(.claude/rules/**)
---

# Overview

Refactor a CLAUDE.md toward progressive disclosure. Every line it keeps is loaded into every session the file covers, and a frontier model follows only around 150 to 200 standing instructions consistently, so each line competes for that budget. Everything else moves down the ladder or out of the file.

## Instructions

1. **Pick the target.** If the invocation names one, use it. Otherwise ask with `AskUserQuestion`, one option per file that exists, with the resolved path in the label:
   - The user-level CLAUDE.md at `~/.claude/CLAUDE.md`
   - The current project's CLAUDE.md

2. **Fetch the yardsticks.** Fetch these pages. They calibrate the delete and rewrite verdicts below:
   - https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
   - https://www.aihero.dev/a-complete-guide-to-agents-md
   - The page for the model this session runs on:
     - Fable 5.1: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
     - Opus 5: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5

3. **Audit.** Read the file and give every instruction exactly one verdict, judged against the target's bar below. Done when no instruction lacks one.
   - **contradiction**: conflicts with another instruction. Record both sides.
   - **delete**: fails the no-op test, meaning the model this session runs on would behave the same without it, or the fetched model page says to remove it because it was written for an earlier model's habits. Judge defaults against that page, not memory. Covers instructions the model already follows by default, instructions too vague to act on, and platitudes like "write clean code".
   - **demote**: real instruction that only applies to some paths or tasks. Pick its destination from the bar. If it describes a multi-step workflow, propose a skill instead. Name the destination in the sign-off.
   - **rewrite**: right meaning, phrasing falls short of the fetched best practices.
   - **keep**: earns its always-loaded cost as written.

   The bar per target:
   - **User-level** (loaded into every session in every project): a keep must apply across all projects. Demote destination: a `paths:`-scoped file in `~/.claude/rules/`.
   - **Project-level** (loaded into every session in this project): a keep must be underivable from the code: a one-sentence project description, commands the agent would guess wrong, domain concepts, gotchas. Lines restating what the code already shows, and volatile detail like file trees, are deletes because they go stale and stale lines poison the context. Demote destinations: a `paths:`-scoped file in `.claude/rules/`, or a doc file linked from CLAUDE.md.

4. **Get decisions.** One `AskUserQuestion` per contradiction, with each conflicting version as an option. Then present the delete and demote lists and collect sign-off with one `AskUserQuestion`. The file stays untouched until sign-off.

5. **Rewrite.** Apply the signed-off verdicts in one pass, without asking again; they are the request. Apply only those: anything else noticed while editing is a follow-up to report in the final message. When creating a new rules file, fetch https://code.claude.com/docs/en/memory#path-specific-rules for the `paths:` frontmatter syntax. Done when every audited instruction landed where its verdict says: kept, rewritten, demoted, or deleted.
