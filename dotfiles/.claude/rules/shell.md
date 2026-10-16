---
paths:
  - "**/*.sh"
  - "**/*.bash"
---

# Shell (bash/zsh)

Scripts target macOS. Shebang `#!/usr/bin/env bash` picks up Homebrew's bash 5.x; system `/bin/bash` is 3.2 and lacks `mapfile`, `${var@Q}`, `inherit_errexit`. macOS ships BSD userland, so `sed`, `date`, `stat`, `mktemp`, `find`, `readlink`, `xargs` differ from GNU. When a script must also run on Linux, either stick to POSIX or `brew install coreutils` and call the `g`-prefixed binaries (`gsed`, `gdate`, `gstat`).

- In a script you execute, use `set -Eeuo pipefail` with `shopt -s inherit_errexit nullglob`; a sourced file leaves shell options to the shell that sources it. Without `-E` and `inherit_errexit`, errors inside `$(...)` and in functions reached from traps are silently swallowed. Skip `IFS=$'\n\t'` — quoted expansions already prevent word-splitting and the narrow IFS surprises downstream tools.
- `set -e` is not error handling: it turns off inside `if`, `while`, `&&`, `||` conditions and in functions reached from those contexts. Add an `ERR` trap reporting `$LINENO` and `$BASH_COMMAND`, plus a cleanup `trap ... EXIT` for temp state.
- Separate stages with one blank line: setup from work, each commented step from the next, a test's arrange from its `run` and assertions. Shell has no types or block keywords to show structure, so blank lines are what a reader scans for.
- When a script grows past ~50 lines or needs arrays of structured data, JSON parsing, or real error types, rewrite it in Python with `uv run` (inline PEP 723 `# /// script` block for deps).
