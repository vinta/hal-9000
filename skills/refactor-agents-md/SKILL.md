---
name: refactor-agents-md
description: Use when about to refactor or refine a user-level or project-level AGENTS.md or CLAUDE.md, from a full restructure down to a one-line wording fix; a change that looks too small to need this skill is not an exemption
argument-hint: [user | project | path/to/AGENTS.md or CLAUDE.md]
allowed-tools:
  - WebFetch(domain:platform.claude.com)
  - WebFetch(domain:code.claude.com)
  - WebFetch(domain:developers.openai.com)
  - WebFetch(domain:learn.chatgpt.com)
  - Edit(AGENTS.md)
  - Edit(CLAUDE.md)
  - Read(~/.claude/CLAUDE.md)
  - Read(~/.codex/AGENTS.md)
---

# Overview

Refactor an instruction file (`AGENTS.md` or `CLAUDE.md`). Every line it keeps is loaded into every session the file covers, and a frontier model follows only around 150 to 200 standing instructions consistently, so each line competes for that budget. Everything else moves down the ladder or out of the file.

The file serves every agent and model that reads it, not only this session's. The filename does not say who reads it, since Claude Code reads `AGENTS.md` too. Each reader assembles its own system prompt, so a line that restates one reader's prompt can be the only copy for another. Audit each line against every reader.

## Instructions

Use `AskUserQuestion` in Claude Code or `request_user_input` in Codex when available.

1. **Pick the target and its readers.** If the invocation names a file, use it. Otherwise ask, one option per file that exists among `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, and the project's `CLAUDE.md` and `AGENTS.md`, with the resolved path in the label. Then settle the readers: the ones the invocation names, otherwise ask in the same question call, multi-select, with the Claude models the user runs and GPT-6 Astra as options, this session's model first. Read one reference per reader platform, both when both read the file:
   - **Claude models:** [references/claude-code.md](references/claude-code.md) for which files load and when, its guides, its system-prompt probe, and its demote destinations.
   - **GPT-6 Astra:** [references/codex.md](references/codex.md) for the same, plus the GPT-6 checks.

   For a targeted change, the verdicts below cover only the lines it adds or touches: the rest of the file stays as it is, and anything noticed there is a follow-up.

2. **Fetch the guides.** Fetch the pages each loaded reference lists. They calibrate the delete and rewrite verdicts below.

3. **Audit.** Read the file and give every instruction in scope exactly one verdict, judged against the target's bar below. Done when no instruction in scope lacks one.
   - **contradiction**: conflicts with another instruction, or the readers' guides pull it opposite ways: one says to remove it while another reader still needs it, or no single wording satisfies every guide. Record both sides.
   - **delete**: fails the no-op test on every reader, meaning each would behave the same without it, or a guide says to remove it because it was written for an earlier model's habits and no other reader needs it either. Judge defaults against the fetched pages and the reference's probe, not memory. Covers instructions the readers already follow by default, instructions too vague to act on, and platitudes like "write clean code". A line any reader needs is a keep.
   - **demote**: real instruction that only applies to some paths or tasks. Pick its destination from the references; it must load for every reader of the source file, and with no such destination the line is a keep. If it describes a multi-step workflow, propose a skill instead. Name the destination in the sign-off.
   - **rewrite**: right meaning, phrasing falls short of the fetched best practices. Also a rewrite when the line carries words that fail the no-op test on their own: a duplicate of another line, a definition of a term the model knows, or emphasis; a rationale or example stays, since both steer the model. Among wordings that pass the bar, the shortest wins. Where a reader's guide gives measured wording for the same instruction and every other reader's guide allows it, use that wording. Voice follows the system prompt: a line addresses the model as "you" and names the human as "the user", so "I" or "my" for the human, and "Claude" or "the agent" for the model, are rewrites; words quoted as user speech keep their own voice.
   - **keep**: earns its always-loaded cost as written, and no shorter wording has the same effect.

   A delete that rests on the shipped system prompt already saying the same thing needs the probe evidence from `references/claude-code.md` for each Claude reader.

   The bar per target:
   - **User-level** (loaded into every session in every project): a keep must apply across all projects.
   - **Project-level** (loaded into every session in this project, or in its directory's subtree for a nested file): a keep must be underivable from the code: a one-sentence project description, commands the readers would guess wrong, domain concepts, gotchas. Lines restating what the code already shows, and volatile detail like file trees, are deletes because they go stale and stale lines poison the context.

4. **Get decisions.** Reuse changes and verdicts the user already authorized. Resolve contradictions from instruction priority and explicit user intent where possible; for each unresolved one, ask with `AskUserQuestion` or `request_user_input`, single-select, each conflicting version an option. Present any remaining delete and demote proposals, with the per-reader probe result beside each prompt-dependent delete, and collect sign-off with one more question. Preserve explicit review boundaries and leave unapproved proposals untouched.

5. **Rewrite.** Apply the signed-off verdicts in one pass, without asking again; they are the request. Apply only those: anything else noticed while editing is a follow-up to report in the final message. Search references before removing or moving guidance, and update affected pointers. Done when every audited instruction landed where its verdict says: kept, rewritten, demoted, or deleted.
