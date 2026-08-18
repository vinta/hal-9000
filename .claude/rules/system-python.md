---
paths:
  - "bin/**"
  - "dotfiles/**"
  - "plugins/**"
  - "skills/**"
  - "pyproject.toml"
  - "Makefile"
  - ".github/workflows/run-tests.yml"
---

# System Python Scripts

- **Python under `bin/`, `dotfiles/`, `plugins/`, and `skills/` must work on Python 3.9**: those directories reach other people's machines, and there `python3` is whatever the OS ships. A stock macOS still ships 3.9. Write them with `from __future__ import annotations` and no 3.10+ stdlib APIs.
- **Everywhere else follows the project floor**: `.claude/`, `scripts/`, and `tests/` only ever run inside this checkout. Put a maintainer-only script there rather than in the four directories above, even when a hook or a skill starts it with a bare `python3`.
- **Location is the declaration, and it is enforced by glob**: `[tool.ruff.per-file-target-version]` and the `vermin` commands in `lint-python` and in the `system-python-tests` job all take those directories rather than file lists, so a new script inherits its floor from where it lands. Moving a script between directories changes which floor applies, silently.
- **The 3.9 job installs its own `pytest`**: the project's `pytest` requires 3.10 or newer, so that job pins an 8.x release with `pip` instead. Bump it on its own schedule and don't unify it with the project's version.
- **The shebang does not choose the interpreter for hook-run scripts**: the hooks in `settings.json` and in each plugin's `hooks.json`, and the statusline command, all name `python3` themselves, so only `bin/hal.py` is executed through its shebang, via the `bin/hal` symlink on `PATH`. Change a command string to change the interpreter; editing a shebang does nothing.
- **`requires-python` does not govern any of this**: it constrains uv's resolution and the interpreter for `.venv`, and ruff and ty infer their targets from it. The gap between the project floor and the `py39` globs is deliberate, so don't align the two.
