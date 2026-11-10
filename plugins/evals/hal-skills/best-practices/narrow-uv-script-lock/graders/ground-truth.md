---
type: llm
---

PASS if the reply states at least two of these documented facts, in any wording:
(a) unlike a uv project, a script is not locked automatically: it has to be locked explicitly, with `uv lock --script <file>` (or an equivalent explicit lock step);
(b) the lockfile is written next to the script under the script's own name, such as `example.py.lock` (not `uv.lock`), and once it exists `uv run --script` (or `uv add`, `uv export`, `uv tree` with `--script`) reuses it;
(c) an `exclude-newer` setting in the `[tool.uv]` table of the inline metadata limits resolution to distributions released before a given date (a timestamp such as `2023-10-16T00:00:00Z`), as a further reproducibility measure.
FAIL if it states fewer than two of them, or contradicts any of them, for example by saying `uv run` creates the script's lockfile on its own, or that the script's lock goes into `uv.lock`.
