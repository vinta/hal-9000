---
type: llm
focus: { source: file, path: skills/deps-audit/SKILL.md }
---

The original step 3 read: "Never fetch a changelog from a mirror or an aggregator, except when the project's own site is down."
PASS only if the file still rules out mirrors and aggregators as changelog sources unless the project's own site is down, in any wording, and adds nothing the original did not say, such as how to tell the site is down, retries, or what to do when both fail.
FAIL if that rule or its exception is gone, a new instruction or reason was added to it, or the file is missing.
