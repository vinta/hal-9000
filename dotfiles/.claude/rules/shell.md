---
paths:
  - "**/*.sh"
  - "**/*.bash"
---

# Shell (bash)

Scripts target macOS and its system bash 3.2 (`#!/usr/bin/env bash`), so avoid `mapfile`, `declare -A`, `${var,,}`, `${var@Q}` and `inherit_errexit`, and expand an array that may be empty as `${arr[@]+"${arr[@]}"}`, since `"${arr[@]}"` aborts under `set -u`. macOS ships BSD userland, so `sed`, `date`, `stat`, `mktemp`, `find`, `readlink`, `xargs` differ from GNU; check a command meant for a script against `/usr/bin/find` and `/usr/bin/grep`, since Claude Code's Bash tool wraps both in shell functions. When a script must also run on Linux, stick to POSIX, or pick each GNU binary per platform: `gdate`/`gstat` from `coreutils`, `gsed` from `gnu-sed`, `gfind`/`gxargs` from `findutils` on macOS, the plain names on Linux.

- In a script you execute, use `set -Eeuo pipefail` with `shopt -s nullglob`; a sourced file leaves shell options to the shell that sources it. `-E` makes the `ERR` trap fire inside functions. A failure inside `$(...)` stops the script only when the substitution is a standalone assignment (`out=$(cmd)`), never inside an argument or after `local`, `export`, `declare` or `readonly`, and only the last command in it counts. Skip `IFS=$'\n\t'` — quoted expansions already prevent word-splitting and the narrow IFS surprises downstream tools.
- `set -e` is not error handling: it turns off inside `if`, `while`, `&&`, `||` conditions and in functions reached from those contexts. Add an `ERR` trap reporting `$LINENO` and `$BASH_COMMAND`, plus a cleanup `trap ... EXIT` for temp state.
- Separate stages with one blank line: setup from work, each commented step from the next, a test's arrange from its `run` and assertions. Shell has no types or block keywords to show structure, so blank lines are what a reader scans for.
- When a script grows past ~50 lines or needs arrays of structured data, JSON parsing, or real error types, rewrite it in Python with `uv run` (inline PEP 723 `# /// script` block for deps).
