---
paths:
  - "**/*.py"
  - "**/pyproject.toml"
---

# Python

- When choosing a Python library or tool, search online and check https://awesome-python.com/llms.txt for curated alternatives before picking one
- Prefer the standard library over adding a dependency (supply-chain hardening) — `urllib.request` over `requests`, `tomllib` over `tomli`, `pathlib` over external path libs
- Before adding a dependency, search PyPI or the web for the latest version
- Pin exact dependency versions in `pyproject.toml` — no `>=`, `~=`, or `^` specifiers
- Target Python >=3.13 by default — if a project sets an explicit version (e.g. `requires-python` in `pyproject.toml`), follow that instead
- Scripts run by system `python3` must work on Python 3.9 — add `from __future__ import annotations` and avoid 3.10+ stdlib APIs
- Use `uv` for project and environment management
  - `uv run` instead of `python3` — picks up the project venv and dependencies automatically
  - New projects: set `exclude-newer = "3 days"` in `[tool.uv]`, use `uv sync --locked` in CI and install scripts to mitigate supply-chain attacks
  - Add `no-build = true` to `[tool.uv]` only when the project has no `[build-system]` — otherwise it blocks the project's own editable install
- Use `ruff` for linting and formatting
- Use `pytest` for testing
  - `assert` is fine in tests but use `# noqa: S101 assert` elsewhere
- Use `TypedDict` for structured dicts — not plain dicts or dataclasses
- When the linter flags something, read the rule it enforces (`ruff rule <CODE>` or the ruff docs). If the rule makes sense for this project, follow it. Suppress with `# noqa` only when the rule does not apply to this project
  - All `# noqa` comments must include the rule name: `# noqa: S603 subprocess-without-shell-equals-true` or `# noqa: S603 PLW1510 subprocess-without-shell-equals-true subprocess-run-without-check` if multiple rules
- Use the `ty` LSP tool for code navigation when grep's text matching would be ambiguous
