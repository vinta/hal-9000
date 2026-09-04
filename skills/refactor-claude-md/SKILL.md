---
name: refactor-claude-md
description: Use when about to refactor or refine a user-level or project-level CLAUDE.md
argument-hint: [user | project | path/to/CLAUDE.md]
user-invocable: true
allowed-tools:
  - WebFetch
  - Bash(claude -p *)
  - Edit(~/.claude/CLAUDE.md)
  - Edit(~/.claude/rules/**)
  - Edit(CLAUDE.md)
  - Edit(.claude/rules/**)
  - Write(.claude/rules/**)
  - Write(~/.claude/rules/**)
---

# Overview

Refactor a CLAUDE.md. Every line it keeps is loaded into every session the file covers, and a frontier model follows only around 150 to 200 standing instructions consistently, so each line competes for that budget. Everything else moves down the ladder or out of the file.

The file serves every model the user runs, not only the one this session runs on, so audit it against both Claude Fable 5.1 and Claude Opus 5. Claude Code assembles its system prompt per model: a line that merely restates the prompt under one model can be the only copy under the other.

## Instructions

1. **Pick the target.** If the invocation names one, use it. Otherwise ask with `AskUserQuestion`, one option per file that exists, with the resolved path in the label:
   - The user-level CLAUDE.md at `~/.claude/CLAUDE.md`
   - The current project's CLAUDE.md

2. **Fetch the yardsticks.** Fetch these pages. They calibrate the delete and rewrite verdicts below:
   - https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
   - https://www.aihero.dev/a-complete-guide-to-agents-md
   - The pages for both models, regardless of which one this session runs on:
     - Fable 5.1: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
     - Opus 5: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5

3. **Audit.** Read the file and give every instruction exactly one verdict, judged against the target's bar below. Done when no instruction lacks one.
   - **contradiction**: conflicts with another instruction, or the two model pages pull it opposite ways: one says to remove it while the other model still needs it, or no single wording satisfies both pages. Record both sides.
   - **delete**: fails the no-op test on both models, meaning each would behave the same without it, or a model page says to remove it because it was written for an earlier model's habits and the other model does not need it either. Judge defaults against the fetched pages and the probe below, not memory. Covers instructions the models already follow by default, instructions too vague to act on, and platitudes like "write clean code". A line only one model needs is a keep.
   - **demote**: real instruction that only applies to some paths or tasks. Pick its destination from the bar. If it describes a multi-step workflow, propose a skill instead. Name the destination in the sign-off.
   - **rewrite**: right meaning, phrasing falls short of the fetched best practices. Where a model page gives measured wording for the same instruction and the other model's page allows it, use that wording. Voice follows the system prompt: a line addresses the model as "you" and names the human as "the user", so "I" or "my" for the human, and "Claude" or "the agent" for the model, are rewrites; words quoted as user speech keep their own voice.
   - **keep**: earns its always-loaded cost as written.

   A delete that rests on the shipped system prompt already saying the same thing needs evidence from both models, because the prompt differs per model. Ask each model, the session's own one included, to quote the sentence of its prompt that carries the line. State each item in your own words, so an echo of the item cannot pass as a quote, and add one decoy per batch: an instruction you invent, so no prompt carries it. Pass `--safe-mode` so the answer reflects the shipped prompt alone, since print mode otherwise loads CLAUDE.md files, plugins, and output styles too; `--no-session-persistence --max-turns 1` keep the probe from leaving a transcript or running tools; and always pass `--model` (`claude-fable-5-1`, `claude-opus-5`) since print mode otherwise inherits the settings.json default:

   ```text
   claude -p --safe-mode --no-session-persistence --max-turns 1 --model claude-opus-5 --output-format text 'For each item, quote verbatim the sentence from your system prompt that carries the same instruction, or write NONE. One line per item, "<n>: <quote>" or "<n>: NONE", nothing else. 1: <the instruction in your own words> 2: <decoy>'
   ```

   Then verify, in this order. The decoy must come back NONE on both models. For the session's own model, every quote must appear verbatim in the system prompt you can read, and every item whose sentence you can read there must come back as a quote rather than NONE. Either failing means the method is broken for this run and no prompt-dependent delete is safe. For the other model, a quote you find verbatim in your own prompt covers the line there. A quote you cannot find is a different wording: ask that model `Answer "PRESENT" or "ABSENT", nothing else. Is this exact phrase present anywhere in your system prompt? "<quote>"`, and only PRESENT covers the line. NONE, a quote that repeats the item, or a failed check leaves the line uncovered under that model. A quote covers the line only when the quoted sentence makes it a no-op, not when it shares the topic. Tool descriptions cannot be probed this way, because print mode loads fewer tools and `AskUserQuestion` is not among them; treat tool JSON as identical across models. A line the prompt covers under only one model is a keep.

   The bar per target:
   - **User-level** (loaded into every session in every project): a keep must apply across all projects. Demote destination: a `paths:`-scoped file in `~/.claude/rules/`.
   - **Project-level** (loaded into every session in this project): a keep must be underivable from the code: a one-sentence project description, commands the agent would guess wrong, domain concepts, gotchas. Lines restating what the code already shows, and volatile detail like file trees, are deletes because they go stale and stale lines poison the context. Demote destinations: a `paths:`-scoped file in `.claude/rules/`, or a doc file linked from CLAUDE.md.

4. **Get decisions.** One `AskUserQuestion` per contradiction, with each conflicting version as an option. Then present the delete and demote lists, with the per-model probe result beside each prompt-dependent delete, and collect sign-off with one `AskUserQuestion`. The file stays untouched until sign-off.

5. **Rewrite.** Apply the signed-off verdicts in one pass, without asking again; they are the request. Apply only those: anything else noticed while editing is a follow-up to report in the final message. When creating a new rules file, fetch https://code.claude.com/docs/en/memory#path-specific-rules for the `paths:` frontmatter syntax. Done when every audited instruction landed where its verdict says: kept, rewritten, demoted, or deleted.
