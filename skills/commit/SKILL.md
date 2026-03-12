---
name: commit
description: Use when making any git commit. All git add and commit operations must go through this skill, including from subagents and other skills
argument-hint: "[instructions]"
context: fork
user-invocable: true
model: sonnet
allowed-tools:
  - Grep
  - Glob
  - Bash(git status:*)
  - Bash(git diff:*)
  - Bash(git branch:*)
  - Bash(git log:*)
  - Bash(git stash:*)
  - Bash(git add:*)
  - Bash(git restore:*)
  - Bash(git mv:*)
  - Bash(git rm:*)
  - Bash(git apply:*)
  - Bash(git commit:*)
  - Read(//tmp/**)
  - Write(//tmp/**)
  - Edit(//tmp/**)
---

# Overview

Creating clean, atomic commits that follow best practices for version control hygiene. The core principle is **one logical change per commit** - each commit should represent a single, coherent, easily revertable modification that can stand alone.

## User Instructions

Follow any user instructions below. They override the standard workflow when conflicts arise, but never override the Critical Rule — never modify working tree files.

<user_instructions>
**$ARGUMENTS**
</user_instructions>

## Critical Rule

You are a committer, not a coder. The user or another agent wrote this code deliberately — modifying it during the commit would silently alter reviewed work without the author's knowledge.

**Your only job**: stage the exact working tree state and write a commit message that captures why the change was made. Do not invoke other skills, run linters, or perform any action beyond staging and committing.

### Git Command Constraints

Use only these forms — each constraint exists to prevent silent modification of working tree files:

| Command       | Allowed form                            | Forbidden form                        | Why                                       |
| ------------- | --------------------------------------- | ------------------------------------- | ----------------------------------------- |
| `git apply`   | `git apply --cached`                    | `git apply` (without `--cached`)      | Bare apply writes to working tree         |
| `git restore` | `git restore --staged`                  | `git restore` (on working tree files) | Bare restore discards unstaged work       |
| `git reset`   | —                                       | `git reset --hard`                    | Discards uncommitted changes              |
| `git rm`      | Only when user already deleted the file | Any other use                         | Don't remove files the user didn't remove |
| `git mv`      | Only when user already moved the file   | Any other use                         | Don't rename files the user didn't rename |

### Noticing Issues

When you spot something that could be improved (a typo, a smell, a missing test), the correct behavior is:

1. Stage and commit the file **as-is**
2. After committing, surface the observation in your output text

<example>
You see a typo in a variable name while reviewing the diff. Correct behavior:
1. Stage and commit the file as-is
2. After committing, say: "I noticed `reuslt` appears to be a typo for `result` in utils.py:42"

Incorrect behavior: editing the file to fix the typo before or during staging — even a "safe" fix silently changes reviewed work.
</example>

## Workflow

`cd` to the project root before git commands instead of using `git -C`, which obscures working directory state. Execute git commands directly without explanatory preamble. Commit immediately without confirmation prompts (interactive mode is not supported).

1. **Analyze Changes**: Use `git status` and `git diff` to understand all modifications in the working directory. Categorize changes by:
   - STRUCTURAL: Code reorganization, renaming, refactoring without behavior changes
   - BEHAVIORAL: New features, bug fixes, functionality changes
   - DOCUMENTATION: README updates, comment changes, documentation files
   - CONFIGURATION: Build files, dependencies, environment settings

2. **Group Logically**: Organize changes into logical units where each unit:
   - Addresses a single purpose or problem
   - Structure changes to be atomic and easily revertable for safe rollback
   - Would make sense to revert as a unit

3. **Stage Changes**: Use appropriate staging strategy:
   - Whole file: `git add <file>`
   - Hunk-by-hunk: `git diff <file> > /tmp/patch.diff`, edit the patch to keep only specific hunks, then `git apply --cached /tmp/patch.diff`
   - To unstage, use `git restore --staged` (not `git reset --hard`, which discards work)
   - Fallback: If `git apply --cached` fails (malformed patch), stage the whole file with `git add <file>` instead

4. **Handle Pre-commit Hooks**: If hooks complain about unstaged changes:
   - Stash unstaged changes first: `git stash push -p -m "temp: unstaged changes"` (select hunks to stash)
   - Or stash all unstaged: `git stash push --keep-index -m "temp: unstaged changes"`
   - Commit, then restore: `git stash pop`
   - If hooks modify staged files (auto-formatting), re-add the modified files and retry the commit

5. **Create Atomic Commits**: For each logical group:
   - Plain, factual commit messages in conventional format
   - Subject line: what changed (under 72 characters)
   - Body: why — the motivation, problem, or context that makes the diff make sense
   - Commit the working tree state as-is — the user may have made manual edits outside this conversation
   - Use `git commit -m "message"` directly — never use `$()` or heredoc subshells in git commands, as they break `allowed-tools` pattern matching

## Attribution

Include a `Co-Authored-By` footer in every commit message:

If you're an Anthropic Claude model:

```
Co-Authored-By: Claude <noreply@anthropic.com>
```

If you're a Google Gemini model:

```
Co-Authored-By: Gemini <gemini-code-assistant@google.com>
```

Skip if you're not one of the above models.
