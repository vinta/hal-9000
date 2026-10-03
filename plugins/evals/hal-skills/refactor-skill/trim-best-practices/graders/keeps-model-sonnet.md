---
type: llm
---

Step 2 (Parallel Research) of the reviewed skill says to pass `model: sonnet` on each Agent call.
PASS only if the reply gives a verdict that covers that instruction, alone or as part of a group, and the instruction survives: kept, reworded, or merged elsewhere.
FAIL if the reply recommends deleting that instruction, gives no verdict that covers it, or is empty or a refusal.
