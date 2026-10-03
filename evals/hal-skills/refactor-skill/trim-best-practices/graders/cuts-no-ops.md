---
type: llm
---

PASS if the audit marks at least three of these as delete, or as a rewrite that removes them:
(a) the Synthesize step's criteria (deduplicate, rank by authority, flag conflicts, discard stale results);
(b) "Be concrete in each subagent prompt ... Vague prompts produce vague results";
(c) "If a subagent failed or returned empty, note the gap ... Do not block synthesis";
(d) the Context7 quota-limits constraint;
(e) the Present Findings structure that repeats the subagent template's output format.
FAIL if fewer than three are marked for removal.
