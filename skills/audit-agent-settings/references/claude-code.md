# Claude Code

## Ground truth

```bash
curl -sfL https://code.claude.com/docs/en/settings.md -o <scratchpad>/cc-docs-settings.md
curl -sfL https://code.claude.com/docs/en/settings-reference.md -o <scratchpad>/cc-docs-settings-reference.md
curl -sfL https://code.claude.com/docs/en/env-vars.md -o <scratchpad>/cc-docs-env-vars.md
```

Every docs page has a raw markdown mirror at its URL plus `.md`.

`settings-reference.md` holds every key: the table under its `## Settings index` heading is one row per key with purpose, topic, and scope, and each key has a `### \`key\`` entry below. `env-vars.md` lists every variable as one table row under `## Variables`, and that row is its whole entry. Grep both for the full lists; a set key's full entry is its `###` section. Read `settings.md` whole for scope and precedence rules. The first line of each file points to https://code.claude.com/docs/llms.txt, the index of every docs page, for follow-ups such as permission rule syntax, hooks, and sandboxing.

## Config scopes

Read every settings scope that exists: `~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json`, and the OS's managed settings file if present.

Instruction files to read for workflow signals: `~/.claude/CLAUDE.md`, the project `CLAUDE.md`, rules files, and auto-memory.

## Validator

Validate with `claude doctor` after edits and read its `Invalid settings` section, since it exits 0 either way. It reports invalid JSON and values the schema rejects, either of which can make Claude Code skip the whole file, while `python3 -m json.tool` catches only the JSON and passes `{"cleanupPeriodDays": "soon"}`. Which picks land later is in the "When edits take effect" section of `settings.md`.

## Dead-key probe

- The installed CLI binary has the final say on undocumented keys and env vars: `strings -a "$(which claude)" | grep -o -E '.{300}<name>.{300}'`. Zero hits means dead; hits mean live code reads it, and the surrounding minified code tells you what it actually does — read it before proposing any change. Observed both failure modes: a docs-only audit flagged `skipAutoPermissionPrompt` dead while a migration in the binary still read it, and `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` turned out to force every session to start in `default` (manual) permission mode, silently overriding `defaultMode: "auto"` with no warning shown.
- Observed undocumented-but-live key: `skillOverrides` sat on the skills page before the settings page listed it.
- The `$schema` line (`https://json.schemastore.org/claude-code-settings.json`) gives editors validation, but the published schema lags new CLI releases. A schema warning on a recently documented key is not proof of a dead key.

## Leave-alone example

The blanket telemetry kills also disable what `env-vars.md` lists under `## Features that need feature-flag fetching`.
