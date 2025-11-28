---
name: code-search
description: Use when understanding/searching codebases for text patterns or structural code patterns. Provides systematic AST-based approach using ast-grep and fast search using ripgrep for comprehensive code search beyond manual inspection.
allowed-tools: Bash(ast-grep:*), Bash(rg:*), Bash(fd:*)
---

## Overview

Code structure reveals more than surface reading - AST patterns expose hidden relationships, security vulnerabilities, and architectural issues that manual inspection misses.

Use these tools to understand codebases, find usage patterns, analyze impact of changes, and locate specific code constructs. Both tools are significantly faster than traditional `grep` or `find` commands.

The code-search skill provides access to the following powerful search tools:

1. **ast-grep (sg)**: Syntax-aware structural search for finding code patterns based on abstract syntax trees
2. **ripgrep (rg)**: Ultra-fast text search with regex support for finding strings, patterns, and text matches
3. **fd**: Simple and fast file search

## When to Use

Use the code-search skill when:

- Understanding a new codebase (finding entry points, key classes)
- Finding all usages of a function, class, or variable before refactoring
- Locating specific code patterns (error handling, API calls, etc.)
- Searching for security issues (hardcoded credentials, SQL queries, eval usage)
- Analyzing dependencies and imports
- Finding TODOs, FIXMEs, or code comments

Choose **ripgrep** for:

- Text-based searches (strings, comments, variable names)
- Fast, simple pattern matching across many files
- When the exact code structure doesn't matter

Choose **ast-grep** for:

- Structural code searches (function signatures, class definitions)
- Syntax-aware matching (understanding code semantics)
- Complex refactoring (finding specific code patterns)

Choose **fd** for:

- Searching for files by name, extension, or pattern across directories.
- Smart case-insensitive search

## References

- Read [references/ast-grep.md](references/ast-grep.md) for detailed usages of `ast-grep`.
- Read [references/ripgrep.md](references/ripgrep.md) for detailed usages of `ripgrep`.
- Read [references/fd.md](references/fd.md) for detailed usages of `fd`.

## Sources

- https://raw.githubusercontent.com/ast-grep/claude-skill/refs/heads/main/ast-grep/skills/ast-grep/references/rule_reference.md
- https://raw.githubusercontent.com/BurntSushi/ripgrep/refs/heads/master/GUIDE.md
- https://raw.githubusercontent.com/laurigates/dotfiles/refs/heads/main/exact_dot_claude/skills/fd-file-finding/SKILL.md
