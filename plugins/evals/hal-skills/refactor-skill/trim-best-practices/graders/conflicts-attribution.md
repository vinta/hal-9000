---
type: llm
---

Step 3 (Synthesize) of the reviewed skill lists "**Flag conflicts** with attribution (which source said what)." Attribution needs to know which source backed which claim, but the subagent prompt template asks only for a trailing list of sources consulted.
PASS only if the reply recommends deleting that criterion, alone or as part of a group, or points out that the subagent reports cannot support per-claim attribution and recommends tying each claim to its source.
FAIL if the reply keeps the criterion without addressing that gap, gives no verdict that covers it, or is empty or a refusal.
