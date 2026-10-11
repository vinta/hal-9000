---
type: llm
---

The Constraints section of the reviewed skill has the bullet "**Context7 quota limits exist.** If `find-docs` fails with quota errors, fall back to web search only and note the limitation." Subagents make the `find-docs` calls and read only the subagent prompt template, so a fallback in Constraints never reaches them.
PASS only if the reply recommends deleting that bullet, or moving its fallback into the subagent prompt template.
FAIL if the reply keeps the fallback in Constraints or elsewhere outside the template, as written, reworded, or merged with another bullet, gives no verdict that covers it, or is empty or a refusal.
