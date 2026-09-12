---
name: refactor-memory
description: Use when refactoring Claude Code or Codex memories to remove stale or derivable entries, resolve contradictions, promote standing instructions, or reorganize recall. Not for standalone CLAUDE.md, AGENTS.md, or rules cleanup
argument-hint: "[scope | path/to/memory/dir]"
user-invocable: true
allowed-tools:
  - WebFetch
  - Read(~/.claude/**)
  - Edit(~/.claude/projects/**/memory/**)
  - Edit(~/.claude/CLAUDE.md)
  - Edit(CLAUDE.md)
  - Edit(~/.claude/rules/**)
  - Edit(.claude/rules/**)
  - Bash(rm ~/.claude/projects/*/memory/*.md)
---

# Overview

Refactor memories so each entry carries what no lookup returns: a decision, a correction, a measured gotcha. Audit entries within the requested scope; their storage and update mechanism depend on the environment.

## Instructions

1. **Pick the target.** Use the scope or directory the user names, otherwise the platform default below. Load the reference for the active environment before reading memories:

   - **Claude Code:** [references/claude-code.md](references/claude-code.md) for project memory files, index rules, promotion destinations, and direct edits.
   - **Codex:** [references/codex.md](references/codex.md) for shared storage, project filtering, promotion destinations, and session-authorized updates.

   State the storage location and audit scope. A shared directory does not make every entry global.

2. **Read the evidence.** Follow the reference's reading procedure and fetch its official memory guide. Compare entries against applicable loaded instructions, repository files, and current vendor documentation. Inventory the entries in scope before assigning verdicts.

3. **Audit entries.** Give every entry exactly one verdict, with its location and evidence beside it. Done when no entry in scope lacks one.
   - **contradiction**: conflicts with another memory, or with the current instruction or code it describes. Record both sides.
   - **delete**: no future action depends on it. Covers completed work, settled questions, and facts recoverable from code, git history, loaded instructions, or vendor docs. Check each claim by looking: search the repo, read the instruction, fetch the docs page. Delete outright, never rewrite into a done or synced record.
   - **rewrite**: right fact, wrong form: a recall hook disagrees with the body, a reference is broken, a date is relative, or two entries carry one fact and should merge.
   - **promote**: a memory that is really a standing instruction. Name the destination using the platform reference. Promote only instructions that change future behavior and are not already covered there; use a skill for a multi-step workflow. Tool behavior alone is not a standing instruction.
   - **keep**: earns its index line and recall cost as written.

4. **Audit recall.** Apply the platform's index or summary checks. Check discoverability, duplicate claims, scope, and evidence references. Propose the layout changes needed for the entries in scope.

5. **Get decisions.** Present each unresolved contradiction with both sides as choices. Then present numbered delete, rewrite, and promote lists with evidence and the proposed layout. Use the platform's question tool to let the user select the verdicts to apply. Honor choices already made; otherwise leave memories unchanged until the user chooses. A missing answer is not a selection.

6. **Apply and verify.** Apply the selected verdicts through the platform's update mechanism without asking again. Edit managed instruction files at their source. Remove a promoted memory only after its destination carries the instruction. Verify the result using the platform reference and report any pending consolidation separately from completed changes. Anything else noticed while editing is a follow-up.
