---
name: publish-plugins
description: (project) Use when editing any file under skills/ or plugins/ to bump the plugin version and check the manifests before committing
user-invocable: true
model: sonnet
allowed-tools:
  - Glob
  - Read
  - Edit
  - Bash(git:*)
  - Bash(python3:*)
  - Bash(claude plugin validate:*)
metadata:
  internal: true
---

# Publish Plugins

Prepare the repo's plugins for release: work out which ones changed, bump their versions, and check the manifests still describe what is on disk.

Each plugin owns its version in its own `.claude-plugin/plugin.json`, and the repo-root `.claude-plugin/marketplace.json` carries no `version` fields:

| Plugin                    | Manifest                                                     |
| ------------------------- | ------------------------------------------------------------ |
| `hal-skills`              | `skills/.claude-plugin/plugin.json`                          |
| `hal-voice`               | `plugins/hal-voice/.claude-plugin/plugin.json`               |
| `hal-session-auto-rename` | `plugins/hal-session-auto-rename/.claude-plugin/plugin.json` |

## 1. Find the changed plugins

```bash
git diff --name-only origin/main...
```

`skills/**` belongs to `hal-skills`, `plugins/<name>/**` to that plugin. Only the plugins with changes are candidates for a bump.

## 2. Check what is already bumped

For each candidate, compare the working-tree version against `origin/main`:

```bash
git show origin/main:skills/.claude-plugin/plugin.json
```

If a plugin's version already differs from `origin/main`, it was bumped for unreleased work. **Do not bump it again.** Only bump a plugin whose version still matches `origin/main`. Check each candidate independently — a change under `skills/` says nothing about whether `hal-voice` needs a bump.

## 3. Bump

- **Patch** (0.2.0 -> 0.2.1): bug fixes, config changes, style cleanup
- **Minor** (0.2.0 -> 0.3.0): new features, new hooks, new commands
- **Major** (0.2.0 -> 1.0.0): breaking changes to hook behavior or config format

## 4. Check the manifests are in sync

```bash
python3 .claude/skills/publish-plugins/scripts/check_manifest_sync.py
```

The `hal-skills` skill list is duplicated on purpose across `skills/.claude-plugin/plugin.json` and the `hal-skills` entry in `.claude-plugin/marketplace.json`. The script compares both lists against each other and against the skill directories on disk, and exits non-zero listing whatever is missing. Fix the manifests it names, then run it again.

## 5. Validate

```bash
claude plugin validate .
claude plugin validate ./skills
claude plugin validate ./plugins/hal-voice
claude plugin validate ./plugins/hal-session-auto-rename
```

The first call validates the marketplace manifest; the rest validate each plugin manifest.
