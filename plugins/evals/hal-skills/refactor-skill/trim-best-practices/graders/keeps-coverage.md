---
type: llm
---

The subagent prompt template in the reviewed skill asks for "Every pitfall you found, including ones you are uncertain about or consider minor. Your job is coverage; synthesis will rank and filter."
PASS only if the reply gives a verdict that covers that instruction, alone or as part of a group, and the instruction survives: kept, reworded, or merged elsewhere.
FAIL if the reply recommends deleting that instruction, gives no verdict that covers it, or is empty or a refusal.
