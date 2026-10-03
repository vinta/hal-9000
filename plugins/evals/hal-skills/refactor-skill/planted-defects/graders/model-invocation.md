---
type: llm
---

The reviewed skill's frontmatter contains `disable-model-invocation: true`, while `skills/release/SKILL.md` tells the model to run the `deploy-check` skill.
PASS only if the reply points out that another skill invokes `deploy-check` and recommends removing `disable-model-invocation: true` or otherwise resolving that conflict.
FAIL if the reply keeps it, mentions it without recommending a change, recommends a change without mentioning the other skill, never mentions it, or is empty or a refusal.
