---
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git branch:*), Bash(git log:*), Bash(git stash:*), , Bash(git add:*), Bash(git commit:*)
description: git commit separately by relevance
---

## Context

- Current git status: !`git status`
- Current git diff (staged and unstaged changes): !`git diff HEAD`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -10`

## Your task

Based on the above changes, create git commits separately by relevance. **One logical change per commit**.

### Commit Types

- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code restructuring
- `docs:` - Documentation
- `test:` - Tests
- `chore:` - Maintenance

### Separate Commits Example

If you've made a bug fix, added a feature, and updated docs:

```bash
# Commit 1: Bug fix
git add src/auth/login.js
git commit -m "fix: resolve login timeout"

# Commit 2: Feature
git add src/components/Search.js src/hooks/useSearch.js
git commit -m "feat: add search functionality"

# Commit 3: Documentation
git add README.md
git commit -m "docs: update API examples"
```

### Attribution

Include in every commit:

```
🤖 Generated with Claude Code (https://claude.ai/code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Key Commands

- `git add [specific-file]` - Stage only related files
- `git add -p` - Stage parts of a file
- `git stash` - Temporarily save unrelated changes
