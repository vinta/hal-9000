# Codex memory

## Target and evidence

Fetch the [Codex memory guide](https://learn.chatgpt.com/docs/customization/memories). Use the memory directory and update contract supplied in the active session. If no location is supplied, inspect `$CODEX_HOME/memories/`, with `~/.codex` as the default Codex home.

Storage is shared across projects by default. Unless the user names another scope, audit the current project's entries and applicable user preferences. A directory argument selects storage, not an all-project audit. Expand to the whole store only when requested, and preserve the scope of project-specific claims.

Use the supplied memory summary, or read `memory_summary.md` if it was not supplied. Search `MEMORY.md` for the selected project, paths, and topics, then read the matching sections in full. Follow their evidence references only as needed to verify claims. For a whole-store audit, inventory the full registry. Compare with applicable `AGENTS.md` files and the repositories the entries describe.

An entry is a claim or coherent group of claims, not an entire generated file or historical transcript. Identify entries by section and claim text as well as path so a regenerated file's line numbers do not become the only locator.

## Recall and promotion

Check summary hooks against registry entries, duplicates across sections, project scope, and evidence references. Use session-defined formats and limits; Claude's topic-file mapping and startup limits do not apply. Propose changes to generated summaries through the update mechanism below.

When promoting a memory, read the `refactor-agents-md` skill and apply its criteria for what belongs in the destination file. Put universal instructions in the Codex home's `AGENTS.md`, project-wide instructions in the project's `AGENTS.md`, and directory-specific instructions in the nearest applicable nested `AGENTS.md`.

## Decisions

Use `request_user_input` when available to select keep, delete, rewrite, or promote outcomes and resolve contradictory claims. Follow the tool's current question and option limits. For single-choice tools, ask per entry or offer a proposed set; let the user specify numbered exceptions in free text. Use plain text when the tool is unavailable.

## Application and verification

Treat memory files as generated state. Follow the active session's authorized update mechanism instead of editing `MEMORY.md`, summaries, or historical evidence directly. If the session permits only change notes, write a small `<timestamp>-<short-slug>.md` file in its designated notes directory, such as `extensions/ad_hoc/notes/`. Record the selected entries, scope, exact removals or replacements, and evidence. Discover this contract from the session; do not assume the notes extension exists everywhere.

If no authorized update mechanism is available, deliver the concrete change list and state that it has not been applied.

Re-read the written note or other update result. Verify generated memory only after consolidation is observable: check that selected claims changed and stale copies are absent from the relevant registry and summary. Report "change note written; consolidation pending" when only the note exists, and claim completion only when the generated result is verified. Preserve supporting history unless its removal is explicitly authorized by both the user and the update contract.
