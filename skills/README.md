# hal-skills

<img src="icon.svg" width="128" alt="vinta/hal-9000 icon">

Agentic skills sharpened by daily use:

- [commit](commit/SKILL.md): Splits your changes into atomic conventional commits, hunk by hunk if needed
- [pr](pr/SKILL.md): Opens a PR, rewrites a PR, or waits for CI and merges it, in seconds on a cheap model
- [difference](difference/SKILL.md): A shortcut to answer "what's the difference? pros and cons?" very quickly
- [fuck-over-engineering](fuck-over-engineering/SKILL.md): Ranks what to cut in your codebase, deletes only what you pick
- [best-practices](best-practices/SKILL.md): Searches the web for the recommended way and common gotchas
- [blindspot](blindspot/SKILL.md): Turns unknown unknowns into known unknowns, then lets you pick where to explore
- [simple-english](simple-english/SKILL.md): Rewrites text in Global English: plain words, still native-sounding
- [write-like-me](write-like-me/SKILL.md): Drafts or rewrites English prose in my own voice at native fluency
- [audit-claude-settings](audit-claude-settings/SKILL.md): Audits your Claude Code settings against the latest docs
- [refactor-claude-md](refactor-claude-md/SKILL.md): Refactors a CLAUDE.md so every line earns its always-loaded cost
- [refactor-agents-md](refactor-agents-md/SKILL.md): Refactors an AGENTS.md the same way, for Codex
- [refactor-memory](refactor-memory/SKILL.md): Prunes stale Claude Code and Codex memories, applies only what you pick
- [refactor-skill](refactor-skill/SKILL.md): Refactors a skill by simplifying it instead of complicating it
- [update-allowed-tools](update-allowed-tools/SKILL.md): Adds missing `allowed-tools` entries to a skill and drops the ones that grant nothing

```bash
# Claude Code
claude plugin marketplace add vinta/hal-9000
claude plugin install hal-skills@hal-9000

# Codex
codex plugin marketplace add vinta/hal-9000
codex plugin add hal-skills@hal-9000
```

If you want to use them in other coding agents:

```bash
npx skills add vinta/hal-9000
```

## Privacy

These skills collect nothing. A few talk to other services when you run them:

- `pr` pushes your branch and opens, updates, or merges the PR on GitHub, via `git` and `gh`
- `best-practices` sends search queries to Context7 (through the `find-docs` skill) and to web search
- `blindspot` and `difference` send search queries to web search
- `refactor-claude-md` sends lines of your CLAUDE.md to Claude via `claude -p`, on your own account, to check which lines the model already follows
- `audit-claude-settings`, `refactor-claude-md`, `refactor-agents-md`, `refactor-memory`, `refactor-skill`, and `update-allowed-tools` read public docs from Anthropic, OpenAI, and SchemaStore
