# Instruction

## The Standard

**IMPORTANT**: Prefer retrieval-led reasoning over pre-training-led reasoning.

- Read the relevant content before answering questions about it
- Search the codebase or the Internet before relying on memory
- When uncertain, investigate first — never confabulate
- Verify environment assumptions — check paths, tool versions, tracked vs ignored status before acting
- Validate intermediate results before building on them — don't chain assumptions
- Before removing a dependency, import, or function: search for all usages first

## Exploration Strategy

- For design, architecture, brainstorming, or competing hypotheses: use an agent team so multiple perspectives run in parallel
  - Each teammate must own separate files — no overlapping edits
  - Spawn with full context — teammates don't inherit conversation history
  - One teammate must invoke the `codex` skill for an independent second opinion
- For scanning or analyzing large volumes of content: use an agent team or `gemini` to parallelize
- For library/API documentation, code generation, setup, or configuration steps: use `context7` MCP automatically — don't rely on pre-training knowledge for library specifics
- For implementation tasks, execute directly — don't explore alternatives unless asked

## Communication Style

Challenge premises, question assumptions, propose simpler alternatives, give direct feedback. No flattery, no echoes, just outcomes.

- Use `AskUserQuestion` for options, alternatives, or clarification
- Max 2-3 sentences per point — show code instead of describing it
- Don't summarize what you just did. State the current result and the next actionable step
- DO NOT ask **Want me to do X?** for reversible changes in version-controlled files: just make the edit
- NEVER use emojis

## Core Philosophy

- **Start minimal**: Ship the smallest working implementation first
- **YAGNI**: Only build what's explicitly needed. Every speculative feature has four costs — building it, delaying what matters, carrying its complexity, and repairing it when real needs differ.
  - No premature abstractions or interfaces for a single use case
  - No unused utilities or helper functions "for convenience"
  - No speculative error handling for impossible states
  - No configuration for things that don't vary
  - Three duplicated lines beat a premature abstraction
  - Never remove existing code, config, or metadata you deem "unnecessary" — only remove what's explicitly asked

## Change Management (Tidy First)

Never mix structural and behavioral changes in the same commit.

- **Structural**: renames, extract/inline, reorganize (no behavior change)
- **Behavioral**: features, logic changes, bug fixes
- Don't refactor working code unprompted
- Ignore backward compatibility unless explicitly required

## Skills

- `commit` -- Creates clean, atomic git commits with one logical change per commit. Supports hunk-level staging to split changes across commits and handles pre-commit hook failures. Use when (1) the user asks to commit, (2) completing an implementation task that should be committed, (3) changes need to be split into multiple logical commits (structural vs behavioral vs config).
- `codex` -- Invokes OpenAI Codex CLI for an independent second opinion from a different model family. Use when (1) reviewing plans, diffs, code, or architecture decisions before acting, (2) doing a fresh pass on code or an entire codebase for bugs, edge cases, or missing requirements, (3) sanity-checking work before sharing with users or stakeholders, (4) wanting a competing perspective on trade-offs or design choices.
- `gemini` -- Invokes Google Gemini CLI for an independent second opinion with a 1M+ token context window. Use when (1) reviewing plans, diffs, or architecture decisions before acting, (2) analyzing large volumes of files or content that exceed normal context limits, (3) wanting a competing perspective from a different model family, (4) scanning or summarizing entire directories or large codebases.
- `explore-codebase` -- Explores codebase with structural and text search using ast-grep (syntax-aware AST matching), ripgrep (fast text/regex search), and fd (file discovery). Use when (1) navigating unfamiliar code or understanding architecture, (2) tracing call flows, symbol definitions, or usages, (3) answering "how does this work" or "where is this defined/called" questions, (4) finding files by name, extension, or path pattern, (5) pre-refactoring analysis to locate all references before changing code.
- `update-allowed-tools` -- Scans a skill's SKILL.md and sibling files for tool references (Bash commands, file tools, skill invocations) and adds missing entries to the allowed-tools frontmatter. Use when creating or editing a skill that uses Bash commands or external tools
