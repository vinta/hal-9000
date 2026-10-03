---
type: llm
---

The reviewed skill's report-format line ends with an example: "For example: `migrations | fail | 0042_drop_legacy_column drops a column`."
PASS only if the reply gives a verdict that covers the report-format line or its example, and that verdict keeps the example, as written or reworded.
FAIL if the reply recommends cutting the example, gives no verdict that covers the report-format line, or is empty or a refusal.
