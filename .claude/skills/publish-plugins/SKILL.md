---
name: publish-plugins
description: (project) Use when editing any file under skills/ or plugins/ to bump the plugin version and check the manifests
user-invocable: true
model: sonnet
effort: medium
allowed-tools:
  - Glob
  - Read
  - Edit
  - Bash(git:*)
  - Bash(python3:*)
  - Bash(claude plugin validate:*)
  - Bash(npx -y skills@latest add . -l)
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

Every plugin is described twice on purpose: once in its own `.claude-plugin/plugin.json` and once as an entry in `.claude-plugin/marketplace.json`. For each plugin the script checks that

- both describe the same fields with the same values, apart from `version` (plugin.json only) and `source`, `category`, `tags`, `strict`, `defaultEnabled` (marketplace entry only — Claude Code ignores them in a plugin.json)
- every component path either manifest declares exists on disk
- every skill directory in a plugin's root appears in both skill lists

It exits non-zero naming each problem. Fix the manifests it names, then run it again.

## 5. Validate

```bash
claude plugin validate .
claude plugin validate ./skills
claude plugin validate ./plugins/hal-voice
claude plugin validate ./plugins/hal-session-auto-rename
```

The first call validates the marketplace manifest; the rest validate each plugin manifest.

## 6. Check the skills still group for other agents

```bash
npx -y skills@latest add . -l
```

This lists what `npx skills add vinta/hal-9000` will offer, reading the working tree instead of the published repo, and installs nothing. Every skill has to appear under the `Hal Skills` heading with a count matching the `skills` list. A skill listed without that heading means the `hal-skills` marketplace entry lost its `name` or its `skills` array — that CLI reads only the two manifests at the repo root, so it never sees `skills/.claude-plugin/plugin.json`.
