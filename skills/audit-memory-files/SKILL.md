---
name: audit-memory-files
description: Use when auditing Claude Code auto memory, the MEMORY.md index and its topic files, to delete stale or derivable memories, fix inconsistencies, promote standing decisions to rules, and regroup the index. Not for CLAUDE.md or rules files themselves
argument-hint: [path/to/memory/dir]
user-invocable: true
allowed-tools:
  - WebFetch
  - Read(~/.claude/**)
  - Edit(~/.claude/projects/**/memory/**)
  - Edit(~/.claude/rules/**)
  - Edit(.claude/rules/**)
  - Write(~/.claude/rules/**)
  - Write(.claude/rules/**)
  - Bash(rm ~/.claude/projects/*/memory/*.md)
---

# Overview

Audit a project's auto memory. `MEMORY.md` is loaded into every session and each topic file is read on recall, so a memory earns its place only by carrying what no lookup returns: a decision, a correction, a measured gotcha. Everything else spends index lines and recall attention on facts that change no future action.

## Instructions

1. **Pick the target.** If the invocation names a directory, use it. Otherwise use the memory directory named in this session's system prompt, the one holding `MEMORY.md`. Read `MEMORY.md`, every topic file, and what the audit compares against: the loaded CLAUDE.md files, `.claude/rules/`, and `~/.claude/rules/`.

2. **Fetch the yardstick.** Fetch https://code.claude.com/docs/en/memory#auto-memory for the current index load limits, the memory types, and what auto memory is meant to skip.

3. **Audit topic files.** Give every topic file exactly one verdict, with the evidence beside it. Done when no file lacks one.
   - **contradiction**: conflicts with another memory, or with the current state of the rule, CLAUDE.md line, or code it describes. Record both sides.
   - **delete**: no future action depends on it. Covers a memory whose tracked work is done or whose question is settled, and a memory the agent could look up when it matters: in the code, git history, a loaded CLAUDE.md or rules file, or the vendor docs. Check each such claim by looking, not from memory: grep the repo, read the rule, fetch the docs page, since a gotcha measured months ago may be documented now. Delete outright, never rewrite into a done or synced record.
   - **rewrite**: right fact, wrong form: the index hook or `description` disagrees with the body; a `[[link]]` names a filename or a slug no memory carries, since links target the `name:` field; a relative date; two files carrying one fact, which merge into one.
   - **promote**: a `feedback` or `project` memory that is really a standing instruction. Destination by scope: a `paths:`-scoped file in `.claude/rules/` when it applies to some paths in this project, `~/.claude/rules/` when it applies in every project, a skill when it is a multi-step workflow. A `reference` memory about how a tool behaves stays a memory, since rules record decisions, not tool behavior. Name the destination.
   - **keep**: earns its index line and recall cost as written.

4. **Audit the index.** Every `MEMORY.md` line points at a file that exists and every topic file has exactly one line. Measure the file against the load limits from the fetched page. Past about twelve entries, group them under `##` headings by the subject a reader scans for; where headings exist, move each entry whose hook fits another heading better and fold a heading left with one or two entries into its nearest neighbor. Done when each line has a file, each file a line, and no heading holds a stray.

5. **Get decisions.** One `AskUserQuestion` per contradiction, each side an option. Then present the delete, rewrite, and promote lists with the evidence beside each item, plus the proposed index layout, and collect sign-off with one `AskUserQuestion`. Nothing changes until sign-off.

6. **Apply.** Apply the signed-off verdicts in one pass, without asking again; they are the request. Apply only those: anything else noticed while editing is a follow-up to report in the final message. Delete a file and its index line together, and repoint or drop every `[[link]]` that named it. When creating a rules file, fetch https://code.claude.com/docs/en/memory#path-specific-rules for the `paths:` frontmatter syntax, and delete the promoted memory once its rule exists. Done when every verdict landed and `MEMORY.md` matches the directory.
