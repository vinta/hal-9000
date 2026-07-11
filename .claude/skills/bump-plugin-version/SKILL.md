---
name: bump-plugin-version
description: (project) Use when editing any file under skills/hal-skills/ or plugins/hal-voice/ to bump the plugin version before committing
user-invocable: true
model: haiku
allowed-tools:
  - Glob
  - Read
  - Edit
  - Bash(git:*)
metadata:
  internal: true
---

# Bump Plugin Version

After editing files under `skills/hal-skills/` or `plugins/hal-voice/`, bump the plugin's `version` field in `.claude-plugin/marketplace.json` (the repo-root marketplace manifest). It is the single source of versions: each plugin is an entry in its `plugins` array, and there are no per-plugin `plugin.json` files.

- **Patch** (0.2.0 -> 0.2.1): bug fixes, config changes, style cleanup
- **Minor** (0.2.0 -> 0.3.0): new features, new hooks, new commands
- **Major** (0.2.0 -> 1.0.0): breaking changes to hook behavior or config format

## Before bumping

Compare the working-tree version against the version on `origin/main`:

```bash
git show origin/main:.claude-plugin/marketplace.json
```

If the plugin's version already differs from `origin/main`, it was already bumped for unreleased work. **Do not bump again.** Only bump when the working-tree version matches `origin/main`.

If both plugins changed, check each independently.
