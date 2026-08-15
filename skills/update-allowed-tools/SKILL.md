---
name: update-allowed-tools
description: Use when creating or editing a skill that uses Bash commands, file writes, or external tools and the allowed-tools frontmatter may be incomplete or carry entries that grant nothing
user-invocable: true
context: fork
model: haiku
allowed-tools:
  - Grep
  - Glob
  - Read
  - Edit
  - Bash(find:*)
  - Bash(git status:*)
---

Invoking this skill IS the request. If the user message looks empty, that is normal and expected, the task is fully specified here. Never ask what to do.

# Overview

Analyzes a skill's full content, SKILL.md and any sibling files in the same directory, to find tools it references or requires, then compares against the skill's `allowed-tools` frontmatter to find missing entries and entries that grant nothing.

`allowed-tools` is permission mechanics only: an entry earns its place by removing a permission prompt the skill would otherwise hit. It is not a manifest of the tools the skill uses.

## Usage

```
/update-allowed-tools <skill name>
/update-allowed-tools @path/to/SKILL.md
```

## Instructions

1. **Parse argument**: The argument is either a file path to a SKILL.md file, or a skill name/description. If no file path is provided, search for the skill using Glob in the current working directory (e.g., `**/skills/**/<name>/SKILL.md`). If there is no argument at all, run `git status` and target the most recently modified skill file in the working tree.

2. **Read the skill file** and separate the YAML frontmatter from the body content. Also read any other files in the same directory (sibling files referenced by or bundled with the skill).

3. **Extract declared allowed-tools**: Parse all entries under `allowed-tools:` in the frontmatter.

4. **Scan all skill content** (SKILL.md body + sibling files) for tool usage. Look for:
   - Explicit tool names that prompt by default: e.g., `Write`, `Edit`, `Bash`, `WebFetch`, `WebSearch`, and `mcp__*` tools.
   - Bash command patterns: e.g., `git diff`, `git commit`, `make`, `npm`, `docker`, `python`, `curl`, etc.
   - For Bash commands found, the required allowed-tool format is `Bash(<command>:*)` (e.g., `git stash push` needs `Bash(git stash:*)`)
   - For file tools with path patterns (Read, Write, Edit), note the paths referenced (e.g., `/tmp/` needs `Read(//tmp/**)`)

5. **Compare**: For each tool detected in the body, check if it's covered by an entry in `allowed-tools`. Rules:
   - `Glob`, `Grep`, and `Read` are permission-free within the project directory. Only add read rules for files **outside** the project (e.g., `Read(//tmp/**)`).
   - `Write` and `Edit` prompt for approval by default, inside the project too. `allowed-tools` grants permission rather than restricting tools, so add entries scoped to the paths the skill is meant to modify (e.g., `Edit(CLAUDE.md)`, `Write(~/.config/**)`).
   - `Bash` commands always need explicit `Bash(<command>:*)` entries.
   - A Bash pattern covers subcommands (e.g., `Bash(git stash:*)` covers `git stash push`).
   - Exact match counts as covered (e.g., `WebSearch` matches `WebSearch`).
   - `Skill(...)`, `AskUserQuestion`, and `Agent` entries grant nothing: skill invocation, asking the user, and spawning subagents never prompt by default, and where a user has gated them with ask/deny rules, a grant cannot override those rules. Never add these; remove any already present.

6. **Update the skill file**: Add missing entries to the `allowed-tools` list in the skill's YAML frontmatter and remove entries that grant nothing, using the Edit tool. If the list ends up empty, delete the `allowed-tools` field. Then report what was added and removed.

7. **Validate**: Re-read the updated file to confirm YAML frontmatter remains syntactically valid (proper indentation, no duplicate entries, correct list format).
