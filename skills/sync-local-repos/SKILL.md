---
name: sync-local-repos
description: Pull the default branch of every repo in your workspace from origin, then rebase the current branch onto it. Pass `this` to sync only the current repo.
argument-hint: "[this]"
disable-model-invocation: true
allowed-tools:
  - Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/sync_local_repos.py *)
---

# sync-local-repos

1. Pick the folder to sync from the session's working directory:
   - Invoked with `this`: the working directory itself, so only its repo is synced.
   - Working directory not inside a git repo: the working directory, whose repos sit directly inside it.
   - Working directory inside a repo: the folder holding that repo and its sibling repos, normally the parent of its main checkout (`git rev-parse --path-format=absolute --git-common-dir` without the trailing `/.git`). When that folder holds no other repo, the repo is probably linked into the real folder by a symlink: find it with `find ~ -maxdepth 3 -lname <main checkout path> 2>/dev/null` and use the symlink's folder. When neither gives a folder of sibling repos, ask the user which folder to sync.

2. Run the script with that folder and the working directory:

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

5. Report the folder synced, the repos that moved or failed, the branch's old and new tip, the script's tree check, and whether anything was pushed.
