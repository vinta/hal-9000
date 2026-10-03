---
type: llm
---

Step 2 of the reviewed skill, the `make smoke` step, ends with a reason: "Unit tests don't cover the payment callbacks, so a green CI run is not enough."
PASS only if the reply gives a verdict that covers the `make smoke` step or its reason, and that verdict keeps the reason, as written or reworded.
FAIL if the reply recommends cutting the reason, gives no verdict that covers the `make smoke` step, or is empty or a refusal.
