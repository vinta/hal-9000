---
paths:
  - "**/*.py"
  - "**/pyproject.toml"
---

# Python

- Check https://awesome-python.com/llms.txt before choosing a library or tool
- Prefer the standard library over adding a dependency — `tomllib` over `tomli`, `pathlib` over external path libs
  - `requests` is fine since it's the de facto standard
- Version specifiers in `pyproject.toml`: `>=` floors (uv's `add-bounds` default). Reproducibility lives in `uv.lock` + `uv sync --locked`; `==` pins there would duplicate the lockfile and block `uv lock --upgrade`
  - Pin `==` only where no lockfile exists (standalone scripts, requirements.txt)
- Use `uv` for project and environment management; `uv run` instead of `python3`
  - Projects with a `[build-system]` need `no-build = false` in `[tool.uv]` — the global `no-build = true` in `~/.config/uv/uv.toml` merges down and blocks the editable install
- Use `pytest` for testing
- Use `ruff` for linting and formatting
  - Outside tests, `assert` needs `# noqa: S101 assert`
- When the linter flags something, read the rule (`ruff rule <CODE>`) and fix the code. Suppress with `# noqa` only when the rule does not apply to the project
  - Every `# noqa` includes the rule name: `# noqa: S603 subprocess-without-shell-equals-true`, or `# noqa: S603 PLW1510 subprocess-without-shell-equals-true subprocess-run-without-check` for multiple rules
- Use `ty` for type checking
- Use `TypedDict`, not plain dicts, for dict shapes crossing a JSON boundary
