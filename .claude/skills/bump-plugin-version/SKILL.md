---
name: bump-plugin-version
description: (project) Use when editing any file under plugins/hal-skills/ or plugins/hal-voice/ to bump the plugin version before committing
user-invocable: true
model: haiku
allowed-tools:
  - Glob
  - Read
  - Edit
metadata:
  internal: true
---

# Bump Plugin Version

After editing files under `plugins/hal-skills/` or `plugins/hal-voice/`, bump the `version` field in **both** the plugin's `plugin.json` and the marketplace manifest. Both files must stay in sync.

| Plugin     | Files to update                                                                           |
| ---------- | ----------------------------------------------------------------------------------------- |
| hal-skills | `plugins/hal-skills/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` |
| hal-voice  | `plugins/hal-voice/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json`  |

- **Patch** (0.2.0 -> 0.2.1): bug fixes, config changes, style cleanup
- **Minor** (0.2.0 -> 0.3.0): new features, new hooks, new commands
- **Major** (0.2.0 -> 1.0.0): breaking changes to hook behavior or config format

## Before bumping

Compare the working-tree version against the version on `origin/main`:

```bash
git show origin/main:<path-to-plugin.json>
```

If the version already differs from `origin/main`, it was already bumped for unreleased work. **Do not bump again.** Only bump when the working-tree version matches `origin/main`.

If both plugins changed, check each independently.
