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

`cd` to `git rev-parse --show-toplevel` before anything else.

Determine the mode from `$ARGUMENTS`: if it contains "merge", run merge mode. Otherwise, run create mode.

## Create mode

1. `git rev-parse --abbrev-ref HEAD` — abort if `main` or `master`.
2. `gh pr view --json url 2>/dev/null` — if a PR already exists, report its URL and stop.
3. `git push -u origin HEAD`.
4. Gather PR material:
   - `git log --oneline main..HEAD` (fall back to `master..HEAD`)
   - `git diff --stat main..HEAD`
5. Invoke the `hal-skills:write-like-me` skill. Pass as argument: "Write a GitHub PR title and body. Title: one plain-English line, no type prefix, under 72 chars. Body: 1-3 sentences — what changed, why. Nothing else. Material:" followed by the git log and diff stat output from step 4.
6. From `write-like-me`'s output, take the first line as title, the rest as body.
7. `gh pr create --title "<title>" --body "<body>"`.
8. Report the PR URL.

## Merge mode

1. `gh pr view --json url,number,state` — abort if no PR or not open.
2. `gh pr checks --watch` — blocks until all checks complete. Use a 10-minute Bash timeout.
3. If exit code 0 (all checks passed):
   - `gh pr merge --merge --delete-branch`
   - `git switch main && git pull`
   - Delete local branch if it still exists: `git branch -d <branch>`
   - Report: merged, remote and local branches cleaned up.
4. If non-zero (check failed):
   - Run `gh pr checks` once more to list failed checks and their URLs.
   - Report which checks failed. Take no other action.
