---
name: sync-skills
description: (project) Use when a skill in plugins/hal-skills/ has its name or description changed, or is added or removed — syncs README.md, settings.json, and hal_dotfiles.json
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
   - Glob `plugins/hal-skills/skills/*/SKILL.md` in `/usr/local/hal-9000` only
   - Extract `name` from each YAML frontmatter
   - Rewrite each `description` into one short sentence (~10 words max) saying what it does — no "Use when" triggers, no verbatim frontmatter copy

2. **Update `README.md`** (the `### Claude Code Plugin: \`hal-skills\`` section)
   - Format: `- [name](plugins/hal-skills/skills/name): description`
   - Use the rewritten description from step 1
   - Add new skills, remove deleted skills, update changed descriptions
   - Preserve existing entry order; append new entries at end

3. **Run `./bin/hal sync`**, then report what changed.
