---
paths:
  - "**/*.py"
  - "**/pyproject.toml"
---

# Python

- Check https://awesome-python.com/llms.txt before choosing a library or tool.
- Prefer the standard library over adding a dependency.
  - `requests` is fine since it's the de facto standard.
- Lock PEP 723 scripts with `uv lock --script <script>`, not `==` pins; pin `==` only in requirements.txt.
- Use `uv` for project and environment management; `uv run` instead of `python3`.
  - Projects with a `[build-system]` need `no-build = false` in `[tool.uv]` — the global `no-build = true` in `~/.config/uv/uv.toml` merges down and blocks the editable install.
- To upgrade a dependency, raise its floor in `pyproject.toml` and run plain `uv lock`, which moves only what the new floor forces; `uv lock --upgrade` moves every transitive package too.
  - Upgrade a transitive package only for a security advisory (`uv audit`, Dependabot) or a bug the project hits, with `uv lock --upgrade-package <name>`.
- Use `pytest` for testing.
- Use `ruff` for linting and formatting.
- When the linter flags something, read the rule (`ruff rule <CODE>`) and fix the code. Suppress with `# noqa` only when the rule does not apply to the project.
  - Every `# noqa` includes the rule name: `# noqa: S603 subprocess-without-shell-equals-true`, or `# noqa: S603 PLW1510 subprocess-without-shell-equals-true subprocess-run-without-check` for multiple rules.
- Use `ty` for type checking.
- Use `TypedDict`, not plain dicts, for dict shapes crossing a JSON boundary.
