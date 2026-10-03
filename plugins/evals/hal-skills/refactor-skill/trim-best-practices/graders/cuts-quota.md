---
type: llm
---

The Constraints section of the reviewed skill has the bullet "**Context7 quota limits exist.** If `find-docs` fails with quota errors, fall back to web search only and note the limitation."
PASS only if the reply recommends deleting that bullet, or a rewrite that drops it.
FAIL if the reply keeps it, only rewords or widens it, mentions it without recommending a change, gives no verdict that covers it, or is empty or a refusal.
