---
paths:
  - "**/*.py"
  - "**/pyproject.toml"
---

# Python

- When choosing a Python library or tool, check https://awesome-python.com/llms.txt before picking one
- Prefer the standard library over adding a dependency (supply-chain hardening) — `tomllib` over `tomli`, `pathlib` over external path libs
  - `requests` is fine since it's the de facto standard
- Version specifiers in `pyproject.toml`: use `>=` floors (uv's `add-bounds` default)
  - Exact reproducibility lives in `uv.lock` + `uv sync --locked`, so `==` pins in `pyproject.toml` would only duplicate the lockfile and block `uv lock --upgrade`
  - Pin exact `==` versions only where no lockfile exists (standalone scripts, requirements.txt)
- Scripts run by system `python3` must work on Python 3.9 — add `from __future__ import annotations` and avoid 3.10+ stdlib APIs
- Use `uv` for project and environment management
  - `uv run` instead of `python3` — picks up the project venv and dependencies automatically
  - Projects with a `[build-system]` need `no-build = false` in `[tool.uv]` — the global `no-build = true` in `~/.config/uv/uv.toml` merges down and blocks the editable install
- Use `pytest` for testing
- Use `ruff` for linting and formatting
  - `assert` is fine in tests but use `# noqa: S101 assert` elsewhere
- When the linter flags something, read the rule it enforces (`ruff rule <CODE>`) and fix the code
  - Suppress with `# noqa` only when the rule does not apply to the project
  - All `# noqa` comments must include the rule name: `# noqa: S603 subprocess-without-shell-equals-true` or `# noqa: S603 PLW1510 subprocess-without-shell-equals-true subprocess-run-without-check` if multiple rules
- Use `ty` for type checking
- Use `ty` LSP tool for code navigation when grep's text matching would be ambiguous
- Use `TypedDict` for structured dicts — not plain dicts or dataclasses
