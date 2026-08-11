---
name: bump-plugin-version
description: (project) Use when editing any file under skills/ or plugins/ to bump the plugin version and sync the skill lists before committing
user-invocable: true
model: haiku
allowed-tools:
  - Glob
  - Read
  - Edit
  - Bash(git:*)
  - Bash(claude plugin validate:*)
metadata:
  internal: true
---

# Bump Plugin Version

After editing files under `skills/` or `plugins/`, bump the plugin's `version` field in its own `.claude-plugin/plugin.json`. Each plugin owns its version there, and the repo-root `.claude-plugin/marketplace.json` carries no `version` fields:

| Plugin                    | Manifest                                              |
| ------------------------- | ----------------------------------------------------- |
| `hal-skills`              | `skills/.claude-plugin/plugin.json`                   |
| `hal-voice`               | `plugins/hal-voice/.claude-plugin/plugin.json`        |
| `hal-session-auto-rename` | `plugins/hal-session-auto-rename/.claude-plugin/plugin.json` |

- **Patch** (0.2.0 -> 0.2.1): bug fixes, config changes, style cleanup
- **Minor** (0.2.0 -> 0.3.0): new features, new hooks, new commands
- **Major** (0.2.0 -> 1.0.0): breaking changes to hook behavior or config format

## Adding or removing a skill

A skill directory added to or removed from `skills/` has to be added to or removed from two `skills` arrays, which list the same paths on purpose:

- `skills/.claude-plugin/plugin.json` — what Claude Code reads for the plugin's own metadata
- the `hal-skills` entry in `.claude-plugin/marketplace.json` — what `npx skills` reads to group the skills

Verify with `claude plugin validate .` afterwards.

## Before bumping

Compare the working-tree version against the version on `origin/main`:

```bash
git show origin/main:skills/.claude-plugin/plugin.json
```

If the plugin's version already differs from `origin/main`, it was already bumped for unreleased work. **Do not bump again.** Only bump when the working-tree version matches `origin/main`.

If several plugins changed, check each independently.
