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

2. **Update `dotfiles/.claude/CLAUDE.md`**: Replace the `## Skills` section (up to the next `##` heading or EOF) with a regenerated list, sorted alphabetically. Format: `- \`/name\` -- description`

3. **Update `dotfiles/hal_dotfiles.json`**: In the `links` array, replace all entries with `"src"` matching `"{{REPO_ROOT}}/skills/*"` with an entry per discovered skill directory (regardless of `user-invocable`), sorted alphabetically. Format: `{"dest": "{{HOME}}/.claude/skills/<name>/", "src": "{{REPO_ROOT}}/skills/<name>/"}`. Preserve all non-skill entries and the `copies` array as-is.

4. **Run `./bin/hal sync`**, then report what changed.
