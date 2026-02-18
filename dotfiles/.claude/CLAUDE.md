# CLAUDE.md

**IMPORTANT**: Search the codebase and web before relying on pre-trained knowledge.

## Communication Style

- Before any change, outline your approach in 3-5 bullets — what, in what order, how to verify — then execute without asking
- Use `AskUserQuestion` for options, alternatives, or clarifications
- Challenge premises, question assumptions, propose simpler alternatives
- Give direct feedback. No flattery, no echoes, just outcomes
- Max 2-3 sentences per point — show code instead of describing it
- Don't summarize what you just did — state the result and next step
- Don't ask **Want me to do X?** — just edit
- NEVER use emojis

## Exploration Strategy

- Decisions, brainstorming, architecture trade-offs: use `magi`
- Large-volume scanning or analysis: use agent teams with `codex` or `gemini`
- Library/API docs, code generation, setup, config: use `context7`
- Verify environment assumptions — check paths, tool versions, tracked vs ignored status before acting

## Implementation Guide

- **YAGNI**: Only build what's explicitly needed, starting with the minimal working implementation. Every speculative feature has four costs — building it, delaying what matters, carrying its complexity, and repairing it when real needs differ
  - No premature abstractions or interfaces for a single use case
  - No unused utilities or helper functions "for convenience"
  - No speculative error handling for impossible states
  - No configuration for things that don't vary
  - Three duplicated lines beat a premature abstraction
  - Never remove existing code, config, or metadata you deem "unnecessary" — only remove what's explicitly asked
- **One thing at a time**: Each pass is behavioral or structural, never both
  - **Behavioral**: features, logic changes, bug fixes
  - **Structural**: renames, extract/inline, reorganize (no behavior change)
- Don't refactor working code unprompted
- Ignore backward compatibility unless explicitly required
- Before removing a dependency, import, or function: search for all usages first
- NEVER use `git -C`. Always `cd` to project root before git commands.

## Skills

- `magi`: Three-agent deliberation system for competing perspectives
- `codex`: Independent review from OpenAI GPT models
- `gemini`: Independent review from Google Gemini models
- `commit`: Creates clean, atomic git commits
- `explore-codebase`: Searches codebase with ast-grep, ripgrep, and fd
- `update-allowed-tools`: Updates skill allowed-tools frontmatter
