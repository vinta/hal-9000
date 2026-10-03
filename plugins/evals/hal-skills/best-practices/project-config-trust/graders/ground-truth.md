---
type: llm
---

PASS if the reply does both:
(a) warns that a project-local config from a cloned repository is untrusted input that could widen the sandbox, and recommends an explicit trust or approval step, naming at least one tool that does this (such as `direnv allow`, `mise trust`, VS Code Workspace Trust, or Claude Code's folder trust prompt);
(b) warns that because the sandboxed process can write the current directory, it could create or edit its own project config, so the config path must be write-protected inside the sandbox or re-approved when it changes.
FAIL if either warning is missing.
