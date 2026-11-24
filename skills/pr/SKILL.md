---
name: pr
description: "Use when the user explicitly asks to push the current branch and open a PR, rewrite an open PR's body from its commits, or wait for CI and merge it"
argument-hint: "[create | update | merge [PR number or URL]] [part-of <issue>]"
context: fork
model: sonnet
effort: medium
allowed-tools:
  - Bash(git push:*)
  - Bash(git rev-parse:*)
  - Bash(gh pr:*)
  - Bash(gh repo view:*)
---

Invoking this skill IS the request. Your task is fully specified here. Never ask what to do.

Run every command bare, exactly as written below: `git` and `gh` find the repository from any subdirectory, and a `cd` does not carry over to the next Bash call in this fork. A `cd ... &&` or `$()` prefix stops a command matching `allowed-tools`, and the merge then hits the permission gate.

So the shell has to start inside the repository. When a command fails with `not a git repository`, stop and report that the skill has to be invoked from inside the repository, or for merge mode with the PR's URL, which `gh` accepts from any directory. A path in the arguments does not change this.

The user invoked this skill with: "$ARGUMENTS"

Mode comes from the arguments first: `create` means create mode, `update` means update mode, `merge` means merge mode. With none of those three words, including an empty argument, run `gh pr view --json state --jq .state 2>/dev/null` and let its result decide: a non-zero exit (no PR for this branch) means create mode, `OPEN` means update mode, any other state means report that state and stop. Merge mode only ever comes from the argument.

## PR material

Create mode and update mode run these steps where they say "gather PR material":

1. `git log --format='%n%s' --name-only main..HEAD` (fall back to `master..HEAD`). Each commit is a block: its subject, then the files it touched. A flat log next to a branch-wide diff stat lets the writer guess which commit touched which file.

2. The PR describes the net change of the branch. A commit whose subject starts with `Revert "` and the commit it names cancel each other when both sit in the log, as does a later commit that restores what an earlier one removed, and a subject starting with `build: bump` describes no change. Remove those blocks from the log before passing it on.

3. `git branch --show-current`, then `git log --format=%B main..HEAD` (same fallback). Collect the issues the branch fixes from the branch name and the commit messages:
   - A GitHub issue: `#N`, or an issue URL. One in another repository is `owner/repo#N`.
   - An issue in a tracker such as Linear or Jira: a key like `ENG-123`, or a URL that contains one. Branch names carry the key in lowercase, as in `fix/eng-123-login-timeout`; write it in uppercase.

   Skip an issue a commit cites only as related or earlier work. Each remaining issue becomes a `Fix [<issue>](<issue URL>)` line at the end of the body, one per line, no duplicates, such as `Fix [ENG-123](https://linear.app/acme/issue/ENG-123/login-timeout)`. Use an issue URL the branch name or commits carry. Otherwise build a GitHub one from the repository URL `gh repo view --json url --jq .url` prints: `https://github.com/acme/app` gives `Fix [#12](https://github.com/acme/app/issues/12)` and `Fix [octo-org/octo-repo#100](https://github.com/octo-org/octo-repo/issues/100)`. A tracker key with no URL, common when only the branch name carries it, borrows one from an earlier PR body: for `ENG-123`, run `gh pr list --state all --limit 100 --json body --jq '[.[].body | scan("https://[^)\\s]*/ENG-[0-9]+")] | first'` with the key's own prefix in place of `ENG`, and swap the key in the URL it prints, so `https://linear.app/acme/issue/ENG-98` gives `Fix [ENG-123](https://linear.app/acme/issue/ENG-123)`. If it prints nothing, the key stays bare: `Fix ENG-123`. GitHub and Linear close the issue on merge only when a closing word such as `Fix` comes before it; a non-closing word such as `Refs` just links it. So an issue the arguments mark as partly done, as in `part-of ENG-123`, gets `Part of` in place of `Fix`, whether or not the branch names it.

4. Invoke the `write-like-me` skill. Pass as argument: "Write a GitHub PR title and body from the material below. Shape the draft as the title on the first line, a blank line, then the body, and nothing else: the caller splits on the first line, so a label or heading would land in the title. The draft goes straight into the caller's next `gh` command in the same response, never into a reply: a reply with no tool call ends the caller before the PR exists.

Title: one plain-English line under 72 chars that names the change itself, with no `fix:` or `feat:` type prefix. GitHub shows titles as plain text, so write file names bare, without backticks. Body: GitHub renders it as markdown, so wrap every file path, command, flag, and identifier in backticks, at every occurrence. Leave out changes a reviewer would not miss, such as ignore files, asset moves, and personal config tweaks, unless the branch holds nothing else. Body shape depends on how many separate changes are left.

One change: 1-3 sentences of prose, what changed and why, no list.

<example>
Add pr skill for pushing branches and opening PRs

Adds a `pr` skill that pushes the current branch, drafts a PR title and body with `write-like-me`, and opens the PR with `gh`. Wires it into the plugin manifest and marketplace so it ships with `hal-skills`.
</example>

Two or more changes: one `-` item per change, each item 1-3 short sentences stating the change and one before/after example when the change has a visible input and output. Give every item its example, not only the first.

<example>
Move name-suffix into core rules and protect URLs and slashes

- Move `name-suffix` from AI spacing into the core rules.
- URLs are left alone. Anything starting with `http://` or `https://` is hidden from the rules, so `%E4%B8%AD` and `/wiki/CJK#CJK` survive.
- `/` next to CJK never gets spaces anymore. `CJK/CJK` stays `CJK/CJK`, same as `_`. File paths still work: `CJK/homeCJK` becomes `CJK /home CJK`.
</example>

<material>" followed by the log from step 2, then a closing "</material>" line.

5. From `write-like-me`'s output, take the first line as title, the rest as body. Append a blank line and the `Fix` and `Part of` lines from step 3 to the body.

## Push

Create, update, and merge mode run these steps where they say "push the branch", so a branch the remote already has is never pushed again:

1. `git rev-parse HEAD`, then `git rev-parse @{u}`, each alone in its Bash call.
2. If both print the same commit, the remote already has every commit: skip the push.
3. Otherwise, including when `git rev-parse @{u}` fails because the branch has no upstream, run `git push -u origin HEAD` alone in its Bash call. Abort if it fails.

## Create mode

1. `git rev-parse --abbrev-ref HEAD` — abort if `main` or `master`.
2. `gh pr view --json url 2>/dev/null` — if a PR already exists, report its URL and stop.
3. Push the branch.
4. Gather PR material.
5. `gh pr create --title "<title>" --body "<body>"`.
6. Report the PR URL.

## Update mode

1. `gh pr view --json url,state 2>/dev/null` — abort if no PR or not open.
2. Push the branch.
3. Gather PR material.
4. `gh pr edit --body "<body>"` — the title stays as it is.
5. Report the PR URL.

## Merge mode

The arguments may name the PR by number or URL, as in `merge 173` or `merge https://github.com/acme/app/pull/173`. The shell then need not be on the PR's branch, so three things change: put the number or URL right after the subcommand in every `gh pr` command below (`gh pr view 173 ...`, `gh pr checks 173 ...`, `gh pr merge 173 ...`), skip step 2, and in step 3 run only the `gh pr view` command and keep the commit it prints.

1. `gh pr view --json url,number,state,headRefName` — abort if no PR or not open.
2. Push the branch.
3. `git rev-parse HEAD`, then `gh pr view --json headRefOid --jq .headRefOid`. If they differ, GitHub has not seen the push yet and `gh pr checks` would report the old head's runs: wait 15 seconds and compare once more, then abort if they still differ.
4. `gh pr checks --watch` — blocks until all checks complete. Use a 10-minute Bash timeout. If step 2 pushed and it reports no checks yet, the push just queued them: wait 15 seconds and run it again once. If the call times out instead, the checks are still running: run it again with the same timeout, and after a third timeout report the checks still pending and stop.
5. `gh pr checks --json name,bucket,link --jq '.[] | select(.bucket != "pass" and .bucket != "skipping")'`. Its output, not the watch's exit code, decides the merge: `gh pr checks` exits 0 even when a check was cancelled, and a cancelled check never ran.
6. If it prints nothing (every check passed or was skipped):
   - `gh pr merge --merge --delete-branch`. When the arguments named the PR, add `--match-head-commit` with the commit from step 3: no local `HEAD` was compared there, and the flag makes GitHub refuse the merge if the PR's head moved after the checks were read.
   - `git rev-parse --verify --quiet refs/heads/<headRefName from step 1>`, alone in its Bash call. `gh` deletes the local branch and removes its worktree only where the checkout allows, and it reports a finished cleanup only on a terminal, so its silence here proves nothing.
   - Report that the PR is merged, then the local side as that command showed it:
     - No output: no local branch is left, and no worktree of it either, since git refuses to delete a branch a worktree has checked out.
     - A commit: the local branch is still there. If `gh pr merge` printed a `skipping local delete` warning, quote it and the `To finish cleanup` command under it word for word.
     - `not a git repository`: the shell is outside the repository, so a local branch or worktree of the PR, if one exists, is still there.
7. Otherwise, report each check it printed with its bucket and link. Take no other action.
