---
paths:
  - "**/*.py"
---

# Python

- Before adding a dependency, search PyPI or the web for the latest version
- Pin exact dependency versions in `pyproject.toml` — no `>=`, `~=`, or `^` specifiers
- Python >=3.11 — use modern syntax: `X | Y` unions, `match`/`case`, `tomllib`
- Use `uv` for project and environment management
- Use `ruff` for linting and formatting
- Use `pytest` for testing
  - `assert` is fine in tests but use `# noqa: S101 assert` elsewhere
- Use `pathlib.Path` over `os.path`
- `# noqa` comments must include the rule name: `# noqa: S603 subprocess-without-shell-equals-true`
