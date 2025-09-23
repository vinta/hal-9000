---
description: Organize commits so each reflects a logically distinct change.
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git branch:*), Bash(git log:*), Bash(git stash:*), Bash(git add:*), Bash(git mv:*), Bash(git rm:*), Bash(git commit:*)
---

Use `git-commit-organizer` subagent.

## Rules

- **One logical change per commit.**
- At initiation, respond with "I will use `git-commit-organizer` subagent." Suppress all subsequent output unless necessary.
- Upon completion, respond with "Done." No further output is required.
- DO NOT use `y`, just fucking commit!

## Extra Instructions (If Provided)

$ARGUMENTS
