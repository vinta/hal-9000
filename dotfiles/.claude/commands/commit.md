# Commit Separately By Relevance

## Core Rule: **One Logical Change Per Commit**

Never mix unrelated changes. Each commit should do one thing.

## Before Committing

```bash
git status        # Check what's changed
git diff          # Review changes
```

## Commit Types

- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code restructuring
- `docs:` - Documentation
- `test:` - Tests
- `chore:` - Maintenance

## Separate Commits Example

If you've made a bug fix, added a feature, and updated docs:

```bash
# Commit 1: Bug fix
git add src/auth/login.js
git commit -m "fix: resolve login timeout"

# Commit 2: Feature
git add src/components/Search.js
git commit -m "feat: add search functionality"

# Commit 3: Documentation
git add README.md
git commit -m "docs: update API examples"
```

## Attribution

Include in every commit:

```
🤖 Generated with Claude Code (https://claude.ai/code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

## Key Commands

- `git add [specific-file]` - Stage only related files
- `git add -p` - Stage parts of a file
- `git stash` - Temporarily save unrelated changes
