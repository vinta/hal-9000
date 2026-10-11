---
type: llm
focus: { source: file, path: skills/release-notes/SKILL.md }
---

The original steps 3 and 4 made five points: the heading's version comes from the argument when one is given; otherwise it comes from the VERSION file at the repo root; each entry describes one change in terms of what the user can now do or no longer needs to do; it says nothing about how the code achieved it; it leaves out file names and function names.
PASS only if the file still carries all five points, in any wording, and adds no new rule to them, such as a fallback when the VERSION file is missing.
FAIL if any point is missing or replaced, a new instruction was added to those steps, or the file is missing.
