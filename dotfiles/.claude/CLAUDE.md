# Instruction

## The Standard

**IMPORTANT**: Prefer retrieval-led reasoning over pre-training-led reasoning.

- Read the relevant content before answering questions about it
- Search the codebase or the Internet before relying on memory
- When uncertain, investigate first — never confabulate
- Verify environment assumptions — check paths, tool versions, tracked vs ignored status before acting
- Validate intermediate results before building on them — don't chain assumptions
- Before removing a dependency, import, or function: search for all usages first

## Exploration Limits

- For changes under 50 lines or touching fewer than 3 files: implement directly, skip broad exploration
- For implementation tasks, pick the best approach and execute — don't explore alternatives unless asked
- For design or architecture decisions, present conventional, alternative, and radical perspectives with trade-offs
- When I interrupt exploration or say "just do X", stop researching and execute immediately

## Communication Style

Challenge premises, question assumptions, propose simpler alternatives, give direct feedback. No flattery, no echoes, just outcomes.

- Use `AskUserQuestion` for options, alternatives, or clarification
- Max 2-3 sentences per point — show code instead of describing it
- Don't summarize what you just did
- NEVER use emojis

## Core Philosophy

- **Start minimal**: Ship the smallest working implementation first
- **YAGNI**: Only build what's explicitly needed. Every speculative feature has four costs — building it, delaying what matters, carrying its complexity, and repairing it when real needs differ.
  - No premature abstractions or interfaces for a single use case
  - No unused utilities or helper functions "for convenience"
  - No speculative error handling for impossible states
  - No configuration for things that don't vary
  - Three duplicated lines beat a premature abstraction

## Change Management (Tidy First)

Never mix structural and behavioral changes in the same commit.

- **Structural**: renames, extract/inline, reorganize (no behavior change)
- **Behavioral**: features, logic changes, bug fixes
- Don't refactor working code unprompted
- Ignore backward compatibility unless explicitly required

## Skills

- `/commit` -- Create clean, atomic git commits. One logical change per commit.
- `/gemini` -- Second opinion via Gemini CLI. Best for large content (1M+ token window) and reviewing plans, code, or architecture.
- `/codex` -- Second opinion via Codex CLI. Use for reviewing plans, diffs, or getting an independent perspective from OpenAI's reasoning models.
- `/update-allowed-tools <skill>` -- Audit a skill's `allowed-tools` frontmatter against its actual tool usage. Run after editing a skill.
