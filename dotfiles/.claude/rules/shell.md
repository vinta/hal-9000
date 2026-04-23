---
paths:
  - "**/*.sh"
---

# Shell (bash/zsh)

Scripts target macOS. Shebang `#!/usr/bin/env bash` picks up Homebrew's bash 5.x — system `/bin/bash` is still 3.2, so `env bash` matters for any modern feature (`mapfile`, `${var@Q}`, `inherit_errexit`). macOS ships BSD userland, so `sed`, `date`, `stat`, `mktemp`, `find`, `readlink`, `xargs` differ from GNU. When a script must also run on Linux, either constrain to POSIX or `brew install coreutils` and call the `g`-prefixed binaries (`gsed`, `gdate`, `gstat`).

- Use `set -Eeuo pipefail` with `shopt -s inherit_errexit nullglob`. Plain `set -euo pipefail` is incomplete: without `-E` and `inherit_errexit`, errors inside `$(...)` and in functions reached from traps are silently swallowed. Skip `IFS=$'\n\t'` — quoted expansions already prevent word-splitting and the narrow IFS surprises downstream tools
- `set -e` is not a substitute for error handling. It silently turns off inside `if`, `while`, `&&`, `||` conditions, and in functions reached from those contexts. Add an `ERR` trap reporting `$LINENO` and `$BASH_COMMAND`, plus a cleanup `trap ... EXIT` for temp state
- `((i++))` exits 1 when the pre-increment value is 0 and trips `-e`. Use `((i+=1))` or `i=$((i+1))`. Reserve `(( ))` for conditions, use `$(( ))` for assignments
- `pipefail` breaks common idioms: `cmd | head -n1` kills the producer with SIGPIPE, `slow | grep -q foo` exits early on match. Scope `pipefail` to specific pipelines if you rely on these
- Process substitution `<(cmd)` hides exit codes — `set -e` and `ERR` don't fire when commands inside fail. Use a temp file + trap if you need the status
- `mapfile -t arr < <(cmd)` beats `while read` loops (no per-line subshell, no scope traps) but requires bash 4+ — fine under `env bash`, broken under `/bin/bash` 3.2
- `$((08+1))` fails — leading zeros parse as octal. Force base-10: `$((10#$month+1))`
- Inside functions, `readonly` is global-scope. Use `local -r` (or `declare -r` without `-g`) for function-scoped constants
- Temp files: `tmp=$(mktemp)` (or `mktemp -d`) + `trap 'rm -rf "$tmp"' EXIT` + `chmod 600 "$tmp"`. Never build temp paths from `$$` or `$RANDOM` (symlink race). Set `umask 077` at script start when creating user data — macOS default of 022 leaves new files world-readable
- Don't pass secrets via argv; `ps` exposes them to any user on the machine. Use stdin or a chmod-600 mktemp file
- Validate input with a whitelist regex before splicing into shell, SSH commands, or awk programs. Use `printf '%q'` when you must splice untrusted strings. Never `eval` user input
- Run `shellcheck` and `shfmt -d` before committing. All `# shellcheck disable=` directives must include the rule name: `# shellcheck disable=SC2086 double-quote-to-prevent-globbing`. Multiple rules: `# shellcheck disable=SC2086,SC2046 ...`
- Don't suppress SC2155 — `local x=$(cmd)` masks the exit code under `-e`. Split into `local x; x=$(cmd)`
- When a script grows past ~50 lines or needs arrays of structured data, JSON parsing, or real error types, rewrite it in Python with `uv run` (inline PEP 723 `# /// script` block for deps) instead of fighting bash
