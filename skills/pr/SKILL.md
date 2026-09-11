---
name: pr
description: "Use when the user explicitly asks to push the current branch and open a PR, rewrite an open PR's body from its commits, or wait for CI and merge it"
argument-hint: "[create | update | merge]"
user-invocable: true
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

Mode comes from the arguments first: `create` means create mode, `update` means update mode, `merge` means merge mode. With none of those three words, including an empty argument, run `gh pr view --json state --jq .state 2>/dev/null` and let its result decide: a non-zero exit (no PR for this branch) means create mode, `OPEN` means update mode, any other state means report that state and stop. Merge mode only ever comes from the argument.

## PR material

Create mode and update mode run these steps where they say "gather PR material":

1. `git log --format='%n%s' --name-only main..HEAD` (fall back to `master..HEAD`). Each commit is a block: its subject, then the files it touched. A flat log next to a branch-wide diff stat lets the writer guess which commit touched which file.

2. The PR describes the net change of the branch. A commit whose subject starts with `Revert "` and the commit it names cancel each other when both sit in the log, and a subject starting with `chore: bump` describes no change. Remove those blocks from the log before passing it on.

3. `git log --format=%b main..HEAD` (same fallback). Collect every issue number written as `#N` or as a GitHub issue URL. Each one becomes a `Fix #N` line at the end of the body, one per line, no duplicates.

4. Invoke the `write-like-me` skill. Pass as argument: "Write a GitHub PR title and body from the material below. Output the title as the first line, a blank line, then the body, and nothing else: the caller splits on the first line, so a label or heading would land in the title.

Title: one plain-English line under 72 chars that names the change itself, with no `fix:` or `feat:` type prefix. GitHub shows titles as plain text, so write file names bare, without backticks. Body: GitHub renders it as markdown, so wrap every file path, command, flag, and identifier in backticks, at every occurrence. Body shape depends on how many separate changes the branch holds.

One change: 1-3 sentences of prose, what changed and why, no list.

<example>
Add pr skill for pushing branches and opening PRs

Adds a `pr` skill that pushes the current branch, drafts a PR title and body with `write-like-me`, and opens the PR with `gh`. Wires it into the plugin manifest and marketplace so it ships with `hal-skills`.
</example>

Two or more changes: a lead line that counts them, then one `-` item per change, each item 1-3 short sentences stating the change and one before/after example when the change has a visible input and output. Apply this to every change, not only the first.

<example>
Protect URLs and slashes from spacing rules

3 rule changes:

- Move `name-suffix` from AI spacing into the core rules.
- URLs are left alone. Anything starting with `http://` or `https://` is hidden from the rules, so `%E4%B8%AD` and `/wiki/CJK#CJK` survive.
- `/` next to CJK never gets spaces anymore. `CJK/CJK` stays `CJK/CJK`, same as `_`. File paths still work: `CJK/homeCJK` becomes `CJK /home CJK`.
</example>

<material>" followed by the log from step 2, then a closing "</material>" line.

5. From `write-like-me`'s output, take the first line as title, the rest as body. Append a blank line and the `Fix #N` lines from step 3 to the body.

## Create mode

1. `git rev-parse --abbrev-ref HEAD` — abort if `main` or `master`.
2. `gh pr view --json url 2>/dev/null` — if a PR already exists, report its URL and stop.
3. `git push -u origin HEAD`.
4. Gather PR material.
5. `gh pr create --title "<title>" --body "<body>"`.
6. Report the PR URL.

## Update mode

1. `gh pr view --json url,state 2>/dev/null` — abort if no PR or not open.
2. `git log --oneline @{u}..HEAD` — if it lists commits, `git push` so the PR shows them.
3. Gather PR material.
4. `gh pr edit --body "<body>"` — the title stays as it is.
5. Report the PR URL.

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
