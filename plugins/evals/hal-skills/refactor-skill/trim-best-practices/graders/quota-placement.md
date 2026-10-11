---
type: llm
---

The Constraints section of the reviewed skill has the bullet "**Context7 quota limits exist.** If `find-docs` fails with quota errors, fall back to web search only and note the limitation." On the parallel path, subagents make the `find-docs` calls and read only the subagent prompt template, so the fallback in Constraints reaches only the single-library path, where Workflow step 1 has the main agent call `find-docs` itself.
PASS only if the reply addresses that subagent gap: it recommends deleting the bullet, moving or copying its fallback into the subagent prompt template, or keeping the bullet while saying subagents never see it, in any wording such as that subagents read only the template, that the template lacks the fallback, or that the fallback reaches only the main agent's own `find-docs` calls.
FAIL if the reply keeps the fallback, as written, reworded, or merged with another bullet, without saying subagents never see it, gives no verdict that covers the bullet, or is empty or a refusal.
