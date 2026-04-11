---
name: bump-plugin-version
description: (project) Use when editing any file under plugins/hal-skills/ or plugins/hal-voice/ to bump the plugin version before committing
user-invocable: true
model: haiku
allowed-tools:
  - Glob
  - Read
  - Edit
---

# Bump Plugin Version

After editing files under `plugins/hal-skills/` or `plugins/hal-voice/`, bump the `version` field in the changed plugin's `.claude-plugin/plugin.json` using semver.

| Plugin     | Version file                                    |
| ---------- | ----------------------------------------------- |
| hal-skills | `plugins/hal-skills/.claude-plugin/plugin.json` |
| hal-voice  | `plugins/hal-voice/.claude-plugin/plugin.json`  |

- **Patch** (0.2.0 -> 0.2.1): bug fixes, config changes, style cleanup
- **Minor** (0.2.0 -> 0.3.0): new features, new hooks, new commands
- **Major** (0.2.0 -> 1.0.0): breaking changes to hook behavior or config format

Bump once per commit session per plugin, not per file edit. If both plugins changed, bump both.
