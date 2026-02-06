---
name: sync-skills
description: Scans dotfiles/.claude/skills/ for all skills and updates CLAUDE.md and hal_dotfiles.json to match, then runs hal sync. Use this skill automatically after editing any skill name/description or adding/removing skills under dotfiles/.claude/skills/.
context: fork
user-invocable: true
model: haiku
allowed-tools:
  - Glob
  - Read
  - Edit
  - Bash(hal sync:*)
---

# Overview

Discovers all skills in `dotfiles/.claude/skills/`, then updates two files to stay in sync:

- `dotfiles/.claude/CLAUDE.md` -- the `## Skills` section
- `dotfiles/hal_dotfiles.json` -- the `copies` entries for skill directories

Finally runs `hal sync` to deploy changes.

## Instructions

1. **Find the project root**: Use Glob to locate `dotfiles/.claude/skills/*/SKILL.md`. The project root is the repo containing `dotfiles/`.

2. **Read each SKILL.md frontmatter**: For every skill found, extract `name` and `description` from the YAML frontmatter.

3. **Update `dotfiles/.claude/CLAUDE.md`**:
   - Find the `## Skills` section (starts with `## Skills` heading).
   - Replace everything from `## Skills` up to the next `##` heading (or end of file) with a regenerated list.
   - Include all discovered skills.
   - Format each entry as: `- \`/name\` -- description`
   - Sort entries alphabetically by name.
   - Keep a blank line after the heading and after the last entry.

4. **Update `dotfiles/hal_dotfiles.json`**:
   - Read the current file and parse the `copies` array.
   - Replace all `.claude/skills/*` entries with entries for each discovered skill directory (regardless of `user-invocable`).
   - Format each entry as: `{"dest": "{{HOME}}/.claude/skills/<name>/", "src": ".claude/skills/<name>/"}`
   - Sort skill entries alphabetically by name.
   - Preserve all non-skill entries in `copies` (and the entire `links` array) exactly as-is.

5. **Run `hal sync`** to deploy the updated files.

6. **Report** what changed: list any skills added or removed from each file.
