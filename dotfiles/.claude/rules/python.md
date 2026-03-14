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
- Use `TypedDict` for structured dicts (hook inputs, configs) — not plain dicts or dataclasses
- Use keyword-only args (`*`) for optional/config parameters: `def run(cmd, *, shell=True)`
- All `# noqa` comments must include the rule name: `# noqa: S603 subprocess-without-shell-equals-true` or `# noqa: S603 PLW1510 subprocess-without-shell-equals-true subprocess-run-without-check` if multiple rules
