# Commit Recent Changes

Follow the instructions precisely. If it wasn't specified, don't do it.

### Commit Process:

1. RUN: `git add .` to stage all changes
2. RUN: `git commit -m "[message]"` with descriptive commit message

### Commit Message Format:

Use one of these formats based on the type of change:

- `feature: [feature description]` for new features
- `fix: [fix description]` for bug fixes
- `refactor: [refactor description]` for code refactoring
- `docs: [documentation change]` for documentation updates
- `test: [test description]` for test additions/changes
- `chore: [chore description]` for maintenance tasks

### Examples:

- `feature: add user authentication system`
- `fix: resolve null pointer exception in data parser`
- `refactor: simplify database connection logic`
- `docs: update API endpoint documentation`

## Best Practices:

- Atomic commits: Each commit should represent a single, logical change
- Separate unrelated changes: If you discover unrelated changes, commit them separately
- Verify code quality: Ensure code is in a working state before committing
- Pre-commit checks: Do NOT commit if:
  - Tests are failing
  - Code has syntax errors
  - Build is broken
- Always include co-authorship:

```
🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```
