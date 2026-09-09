---
name: pr
description: "Use when ready to push the current branch and open a PR; with `merge`, waits for CI and merges it"
argument-hint: "[create | merge]"
user-invocable: true
disable-model-invocation: true
context: fork
model: sonnet
effort: medium
allowed-tools:
  - Bash(git status:*)
  - Bash(git branch:*)
  - Bash(git log:*)
  - Bash(git diff:*)
  - Bash(git rev-parse:*)
  - Bash(git push:*)
  - Bash(git switch:*)
  - Bash(git pull:*)
  - Bash(gh pr:*)
  - Bash(gh run:*)
---

Invoking this skill IS the request. Your task is fully specified here. Never ask what to do.

Your first Bash call is `cd "$(git rev-parse --show-toplevel)"`, alone, once. The working directory persists across Bash calls, so run every later command bare, exactly as written below. A `cd ... &&` or `$()` prefix stops a command matching `allowed-tools`, and the merge then hits the permission gate.

The user invoked this skill with: "$ARGUMENTS"

Arguments containing `merge` mean merge mode. Anything else, including empty, means create mode.

## Create mode

1. `git rev-parse --abbrev-ref HEAD` — abort if `main` or `master`.
2. `gh pr view --json url 2>/dev/null` — if a PR already exists, report its URL and stop.
3. `git push -u origin HEAD`.
4. Gather PR material:
   - `git log --oneline main..HEAD` (fall back to `master..HEAD`)
   - `git diff --stat main..HEAD`
5. Invoke the `hal-skills:write-like-me` skill. Pass as argument: "Write a GitHub PR title and body. Output the title as the first line, a blank line, then the body, with no labels or headings around them. Title: one plain-English line, no type prefix, under 72 chars, no backticks. Body: 1-3 sentences of prose — what changed, why. No headings, no lists. In the body, wrap every file path, command, flag, and identifier in backticks, at every occurrence, like `plugins/hal-output-styles/plugin.json`, `~/.claude/skills`, `hal sync`, `say-no-more`. Material:" followed by the git log and diff stat output from step 4.
6. From `write-like-me`'s output, take the first line as title, the rest as body.
7. `gh pr create --title "<title>" --body "<body>"`.
8. Report the PR URL.

## Merge mode

1. `gh pr view --json url,number,state` — abort if no PR or not open.
2. `git log --oneline @{u}..HEAD` — if it lists commits, `git push` so CI and the merge see them.
3. `gh pr checks --watch` — blocks until all checks complete. Use a 10-minute Bash timeout. If you pushed and it reports no checks yet, the push just queued them: wait 15 seconds and run it again once.
4. If exit code 0 (all checks passed):
   - `gh pr merge --merge --delete-branch`
   - `git switch main && git pull`
   - Delete local branch if it still exists: `git branch -d <branch>`
   - Report: merged, remote and local branches cleaned up.
5. If non-zero (check failed):
   - Run `gh pr checks` once more to list failed checks and their URLs.
   - Report which checks failed. Take no other action.
