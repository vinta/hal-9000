# Commit Guidelines

## Key Rule: **Separate Unrelated Changes**

Before committing:

1. Run `git status` and `git diff` to review changes
2. Group related changes together
3. Commit each group separately using `git add [specific files]`

## Commit Message Format

- `feature: [description]` - new features
- `fix: [description]` - bug fixes
- `refactor: [description]` - code refactoring
- `docs: [description]` - documentation updates
- `test: [description]` - test changes
- `chore: [description]` - maintenance tasks

## Rules

- One logical change per commit
- Ensure code works before committing
- Don't commit if tests fail or build is broken
- Include co-authorship:

```
🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Example

If you've made a bug fix, added a feature, and fixed a typo:

- Commit 1: `fix: resolve auth timeout`
- Commit 2: `feature: add dashboard widget`
- Commit 3: `docs: fix typo in README`
