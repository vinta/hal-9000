---
name: audit-claude-settings
description: Use when auditing Claude Code settings and env vars against the latest docs and suggest tailored changes
allowed-tools:
  - Bash(curl -sL https://code.claude.com/*)
  - Bash(python3 -m json.tool *)
  - Bash(strings *)
  - Bash(which claude)
  - Bash(git diff:*)
  - Read(~/.claude/**)
  - AskUserQuestion
---

# Audit Claude Code Settings

Scan the two reference pages exhaustively, cross-reference them against the user's real config, deliver a ranked report, and apply what the user picks. Tie every suggestion to a named user fact — tailored, not generic.

## 1. Fetch ground truth

```bash
curl -sL https://code.claude.com/docs/en/settings.md -o /tmp/cc-docs-settings.md
curl -sL https://code.claude.com/docs/en/env-vars.md -o /tmp/cc-docs-env-vars.md
```

Every docs page has a raw markdown mirror at its URL plus `.md`. Write to your session's scratchpad directory instead of `/tmp` when the harness provides one. Verify each download is hundreds of KB; a small file is a failed fetch, not a short page. These two files are the only acceptable source for the scan.

Read both files completely in chunks — the Read tool caps near 25k tokens per call, and each file runs 75–90k tokens. On a small context window, fan each file out to a subagent that returns every key name with a one-line summary, and audit from those lists. The first lines of each file point to https://code.claude.com/docs/llms.txt, the index of every docs page, for follow-ups such as permission rule syntax, hooks, and sandboxing.

## 2. Collect the user's real config

Read every settings scope that exists: `~/.claude/settings.json`, `.claude/settings.json`, `.claude/settings.local.json`, and the OS's managed settings file if present. When a dotfiles repo is the source of truth, read the repo copy and run `git diff` on it — uncommitted drift matters in step 5.

Read `~/.claude/CLAUDE.md`, the project `CLAUDE.md`, rules files, and auto-memory. These carry the workflow signals that make suggestions tailored: plugins, hooks, shell aliases, permission style, model choice, terminal, background-agent habits.

Done when you hold one list of every key and env var the user sets, plus a short profile of how they work.

## 3. Cross-reference

Two passes, both exhaustive:

- **Validate (set → docs).** Check every user key against both files. Absent from both → dead-key candidate; confirm against the binary (see Gotchas) before proposing removal. Named a legacy alias → propose the migration. Default or semantics changed → flag it. No key skipped.
- **Discover (docs → unset).** Walk every documented key and variable once. Keep a candidate only when a specific user fact argues for it, and name that fact in the item.

## 4. Report

Open with problems in the current config, ranked by impact. Then grouped suggestions: security, workflow, small ideas. Close with leave-alone items — attractive switches that break something the user relies on (example: the blanket telemetry kills also disable Remote Control, cross-session messages, and auto-updates).

Each item carries the key, what it does in one line, and the user fact that makes it relevant.

## 5. Apply

Offer the picks with AskUserQuestion, multiSelect, grouped like the report. When the settings file already has uncommitted changes, commit those first as their own commit.

Apply the picks and validate with `python3 -m json.tool` after edits — a user or project settings file with one invalid entry is rejected as a whole. Say which picks land later: `model` and `outputStyle` load at startup only, keys that shape the system prompt land on `/clear` or restart, and `env` entries reload live.

## Gotchas

- WebFetch answers through a small summarizer model. On a "list everything" prompt against a long page it truncates, and on a "continue the list" prompt it fabricates plausible keys (observed: `rubyCrimsionPath`). The raw `.md` mirror is the ground truth; fetch it with curl and read it yourself.
- Undocumented is not the same as dead. A key can live on a different docs page — `skillOverrides` sat on the skills page before the settings page listed it. Grep both files, then check llms.txt pages, before you call a key dead.
- The installed CLI binary is the final arbiter for undocumented keys and env vars: `strings -a "$(which claude)" | grep -o -E '.{300}<name>.{300}'`. Zero hits means dead; hits mean live code reads it, and the surrounding minified code tells you what it actually does — read it before proposing any change. Observed both failure modes: a docs-only audit flagged `skipAutoPermissionPrompt` dead while a migration in the binary still read it, and `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` turned out to force every session to start in `default` (manual) permission mode, silently overriding `defaultMode: "auto"` with no warning shown.
- The `$schema` line (`https://json.schemastore.org/claude-code-settings.json`) gives editors validation, but the published schema lags new CLI releases. A schema warning on a recently documented key is not proof of a dead key.
- Docs churn fast. Results from a previous audit go stale; fetch fresh files every run, and treat remembered page content as expired.
