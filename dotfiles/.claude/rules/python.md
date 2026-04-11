---
paths:
  - "**/*.py"
  - "docs/**/*.md"
---

# Python

- When choosing a Python library or tool, search online and check https://awesome-python.com/llms.txt for curated alternatives before picking one
- Before adding a dependency, search PyPI or the web for the latest version
- Pin exact dependency versions in `pyproject.toml` — no `>=`, `~=`, or `^` specifiers
- Target Python >=3.13 by default — if a project sets an explicit version (e.g. `requires-python` in `pyproject.toml`), follow that instead
- Use the pyright LSP tool for code navigation when grep's text matching would be ambiguous. LSP resolves symbol relationships through the type system, so `findReferences` on a function returns its actual call sites, not every file containing the same string. Reach for LSP when:
  - Tracing all usages before removing or renaming a symbol (`findReferences`)
  - Understanding a function's callers or callees (`incomingCalls` / `outgoingCalls`)
  - Navigating to a symbol's definition (`goToDefinition`)
  - Checking type information at a position (`hover`)
  - Surveying a file's or workspace's structure (`documentSymbol` / `workspaceSymbol`)
- Use modern syntax: `X | Y` unions, `match`/`case`, `tomllib`
- Scripts run by system `python3` must work on Python 3.9 — add `from __future__ import annotations` and avoid 3.10+ stdlib APIs
- Use `uv` for project and environment management
  - `uv run` instead of `python3` — picks up the project venv and dependencies automatically
- Use `ruff` for linting and formatting
- Use `pytest` for testing
  - `assert` is fine in tests but use `# noqa: S101 assert` elsewhere
- Use `pathlib.Path` over `os.path`
- Use `TypedDict` for structured dicts (hook inputs, configs) — not plain dicts or dataclasses
- Use keyword-only args (`*`) for optional/config parameters: `def run(cmd, *, shell=True)`
- All `# noqa` comments must include the rule name: `# noqa: S603 subprocess-without-shell-equals-true` or `# noqa: S603 PLW1510 subprocess-without-shell-equals-true subprocess-run-without-check` if multiple rules
- Use f-strings over `.format()` or `%` formatting
- Use `enumerate()` over `range(len())`
- Prefer comprehensions over `map()` / `filter()` with lambdas
