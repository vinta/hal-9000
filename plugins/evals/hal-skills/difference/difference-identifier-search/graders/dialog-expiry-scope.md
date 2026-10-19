---
type: llm
---

PASS if the reply says `dialogExpiry` applies to dialogs forwarded to a remote client (such as Remote Control or an SDK host) or other non-local prompts, and does not claim it expires or auto-denies the local tool permission prompts in the terminal.
FAIL if the reply says `dialogExpiry` covers ordinary local tool permission prompts, or describes it only from its name without saying which dialogs it covers.
