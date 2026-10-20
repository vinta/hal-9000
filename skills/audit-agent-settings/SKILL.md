---
name: audit-agent-settings
description: Use when auditing Claude Code or Codex settings and env vars against the latest docs to suggest tailored changes
allowed-tools:
  - Bash(curl -sfL https://code.claude.com/*)
  - Bash(curl -sfL https://learn.chatgpt.com/*)
  - Bash(claude doctor)
  - Bash(strings:*)
  - Read(~/.claude/**)
  - Read(~/.codex/**)
---

# Audit Agent Settings

Scan the platform's docs exhaustively, cross-reference them against the user's real config, deliver a ranked report, and apply what the user picks. Tie every suggestion to a named user fact — tailored, not generic.

Use `AskUserQuestion` in Claude Code, with multi-select for several picks. In Codex, use `request_user_input`, which has no multi-select: for several picks, ask one Apply/Skip question per item, three per call. Use plain text when the named tool is unavailable.

## 1. Pick the targets

Use targets already specified by the user. Otherwise, offer the existing targets with this session's platform first: Claude Code settings, Codex config, or both. Read one reference per target:

- [references/claude-code.md](references/claude-code.md) for Claude Code's docs mirrors, settings scopes, validator, dead-key probe, and gotchas.
- [references/codex.md](references/codex.md) for the same on Codex.

Done when every target has its reference loaded.

## 2. Fetch ground truth

Curl each raw markdown mirror the reference lists into `<scratchpad>`. `<scratchpad>` is your session's scratchpad directory, or `/tmp` when the harness provides none. `-f` makes a missing page a failed command instead of a silently saved 404 body. These files are the only acceptable source for the scan; the reference's installed-CLI probes verify behavior, they do not replace the files.

Follow the reference's notes on how keys and variables are laid out in those files, and grep them for the full lists. Read the full entry of every key the user sets, since the entries carry the defaults, deprecations, and precedence the index omits.

## 3. Collect the user's real config

Read every config scope the reference lists, where it exists. When a dotfiles repo is the source of truth, read the repo copy and run `git diff` on it — uncommitted drift matters in step 6.

Read the platform's instruction files, rules, and memory the reference lists. These carry the workflow signals that make suggestions tailored: plugins, hooks, shell aliases, permission style, model choice, terminal, background-agent habits.

Done when you hold one list of every key and env var the user sets, plus a short profile of how they work.

## 4. Cross-reference

Two passes, both exhaustive:

- **Validate (set → docs).** Check every user key against the fetched files. Treat absent, removed, deprecated, or no-effect keys as candidates for the reference's dead-key probe; confirm their installed behavior before proposing removal or migration. Named a live legacy alias → propose the migration. Default or semantics changed → flag it. No key skipped.
- **Discover (docs → unset).** Walk every documented key and variable once, applying the reference's scope restrictions and skipping administrator-only settings unless the user manages that scope. Keep a candidate only when a specific user fact argues for it, and name that fact in the item.

## 5. Report

Open with problems in the current config, ranked by impact. Then grouped suggestions: security, workflow, small ideas. Close with leave-alone items — attractive switches that break something the user relies on (the reference has an example).

Each item carries the key, what it does in one line, and the user fact that makes it relevant.

## 6. Apply

Apply picks already authorized by the user; otherwise, collect picks grouped like the report using the selection method above. Before editing a tracked settings file with uncommitted changes, distinguish user-authored edits from CLI-written changes, following the reference's drift guidance where provided. Commit only identified user-authored edits first as their own commit, honoring explicit commit exclusions; leave automatic or uncertain changes uncommitted.

Apply the picks and validate with the reference's validator after edits. Say which picks land later, per the reference.

## Gotchas

- WebFetch and similar fetch tools answer through a separate model call, not the raw page, and read a long page 100,000 characters per call. The scan greps every key and reads whole entries, which needs the raw text in a file, and a "continue the list" prompt has fabricated plausible keys (observed: `rubyCrimsionPath`). Fetch the raw markdown mirror with curl and read it yourself.
- Undocumented is not the same as dead. A key can live on a different docs page than the fetched files. Grep all the fetched files, then check the platform's other docs pages the reference points to and run its dead-key probe before you call a key dead.
- Docs churn fast. Results from a previous audit go stale; fetch fresh files every run, and treat remembered page content as expired.
