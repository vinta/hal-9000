---
name: sync-local-repos
description: Pull the default branch of every repo in your workspace from origin, then rebase the current branch onto it. Pass `this` to sync only the current repo.
argument-hint: "[all | this]"
disable-model-invocation: true
allowed-tools:
  - Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/sync_local_repos.py *)
---

# sync-local-repos

Use `AskUserQuestion` in Claude Code or `request_user_input` in Codex when available to ask the user anything below.

1. Pick the folder to sync from the session's working directory. The repo's main checkout is `git rev-parse --path-format=absolute --git-common-dir` without the trailing `/.git`.
   - `this`: the main checkout, so only that repo is synced.
   - `all` or no argument, working directory not inside a git repo: the working directory, whose repos sit directly inside it.
   - `all` or no argument, working directory inside a repo: the folder holding the main checkout and its sibling repos, normally the main checkout's parent. When that folder holds no other repo, the repo is probably linked into the real folder by a symlink: find it with `find ~ -maxdepth 3 -lname <main checkout> 2>/dev/null` and use the symlink's folder. When neither gives a folder of sibling repos, ask the user which folder to sync.

2. Run `scripts/sync_local_repos.py` from this skill's folder with that folder and the working directory:

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/sync_local_repos.py "<folder>" "<working directory>"
   ```

   It fast-forwards each main checkout's default branch (`pull --ff-only` when checked out, `fetch origin <def>:<def>` otherwise), then rebases the branch at the working directory onto `origin/<def>`. Done when it exits: 0 means every step succeeded, 1 means a `FAIL` repo line or a `STOP` line.

3. Settle each `FAIL` and `STOP` line:
   - `FAIL` on a repo: report the git error; a checkout whose default branch diverged from origin needs the user's call.
   - `STOP <upstream> has N commits <branch> lacks`: someone pushed work to the branch that this checkout does not have. Report the listed commits and ask the user before pulling them in. A remote that only holds the same commits rebased, or an older copy of them, does not stop the script: it adopts or rebases past them on its own.
   - `STOP uncommitted changes`, `STOP merge commits`, `STOP conflict`: report the files or commits listed and ask the user how to proceed. A conflict was already aborted, so the branch is unchanged.

4. A rebased branch that was already pushed needs a force-push. Ask the user first, then push with a lease on the tip the remote holds, so a teammate's newer push makes it fail:

   ```bash
   git push --force-with-lease=<branch>:<old tip> origin <branch>
   ```

5. When nothing needs the user, report one line: `Synced <folder>: all N repos ok on their default branch`, plus `; rebased <branch> onto origin/<def>` when the branch moved. Otherwise lead with what needs the user (each `FAIL` and `STOP`, a tree check asking for review, a pending force-push), then the repos that moved, the branch's old and new tip, and whether anything was pushed. Never list checks that passed.
