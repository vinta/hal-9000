---
name: sync-skills
description: (hal-9000) Syncs the Skills section in CLAUDE.md and skill entries in hal_dotfiles.json with skills/ directory.
context: fork
user-invocable: true
model: haiku
allowed-tools:
  - Glob
  - Read
  - Edit
  - Bash(hal sync:*)
---

# Instructions

**IMPORTANT**: Only use this skill in `/usr/local/hal-9000`. Otherwise, abort.

1. **Discover skills**: Glob for `skills/*/SKILL.md` rooted at **this repository** (`/usr/local/hal-9000`). Do NOT search any other directory. Extract `name` and `description` from each YAML frontmatter.

2. **Update `dotfiles/.claude/CLAUDE.md`**: In the `## Skills` section (up to the next `##` heading or EOF), add entries for newly discovered skills and remove entries for skills that no longer exist. **Do NOT reorder existing entries — preserve their exact current order.** Append new entries at the end. Format: `- \`name\` -- description`

3. **Update `dotfiles/hal_dotfiles.json`**: In the `links` array, add entries for newly discovered skill directories and remove entries whose `"src"` matches `"{{REPO_ROOT}}/skills/*"` but no longer has a corresponding skill. **Do NOT reorder existing entries — preserve their exact current order.** Append new entries at the end. Format: `{"dest": "{{HOME}}/.claude/skills/<name>/", "src": "{{REPO_ROOT}}/skills/<name>/"}`. Preserve all non-skill entries and the `copies` array as-is.

4. **Run `./bin/hal sync`**, then report what changed.
