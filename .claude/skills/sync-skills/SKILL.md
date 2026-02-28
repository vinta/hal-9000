---
name: sync-skills
description: (hal-9000) Use when a skill in skills/ has its name or description changed, or is added or removed — syncs README.md, settings.json, and hal_dotfiles.json
context: fork
user-invocable: true
model: haiku
allowed-tools:
  - Glob
  - Read
  - Edit
  - Bash(./bin/hal sync:*)
---

# Instructions

**IMPORTANT**: Only use this skill in `/usr/local/hal-9000`. Otherwise, abort.

1. **Discover skills**
   - Glob `skills/*/SKILL.md` in `/usr/local/hal-9000` only
   - Extract `name` from each YAML frontmatter
   - Rewrite each `description` into one short sentence (~10 words max) saying what it does — no "Use when" triggers, no verbatim frontmatter copy

2. **Update `README.md`** (the `### Agent Skills` section)
   - Format: `- [name](skills/name): description`
   - Use the rewritten description from step 1
   - Add new skills, remove deleted skills, update changed descriptions
   - Preserve existing entry order; append new entries at end

3. **Update `dotfiles/.claude/settings.json`** (the `permissions.allow` array)
   - Sync the `Skill(...)` entries to match discovered user-invocable skills
   - Only include skills with `user-invocable: true` in frontmatter
   - Format: `"Skill(<name>)"`
   - Add new skills, remove entries whose skill no longer exists
   - Preserve existing entry order; append new entries at end
   - Keep the entries in the same position block (between other tool entries)

4. **Update `dotfiles/hal_dotfiles.json`** (the `links` array)
   - Format: `{"dest": "{{HOME}}/.claude/skills/<name>/", "src": "{{REPO_ROOT}}/skills/<name>/"}`
   - Add new skill dirs, remove entries whose `"src"` matches `{{REPO_ROOT}}/skills/*` but no longer has a matching skill
   - Preserve existing entry order; append new entries at end
   - Leave non-skill entries and `copies` array as-is

5. **Run `./bin/hal sync`**, then report what changed.
