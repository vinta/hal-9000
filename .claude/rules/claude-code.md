---
paths:
  - ".claude/**"
  - ".claude-plugin/**"
  - "**/CLAUDE.md"
  - "dotfiles/.claude/**"
  - "plugins/**"
  - "skills/**"
---

# Claude Code

- Claude Code moves fast and its docs change under you. Before modifying anything Claude Code related (settings, rules, skills, plugins, marketplaces), fetch the latest docs first: use the per-topic URLs under "Documentation Links" in CLAUDE.md, or discover other pages via the index at https://code.claude.com/docs/llms.txt.
- **Rules record decisions, not documentation**: when writing a rule file or CLAUDE.md entry, each line must state a preference, contract, or deliberate deviation Claude might otherwise "fix" — never how an external tool behaves (that rots when the tool changes, and find-docs covers it) and never a quoted vendor string or version-specific identifier. Where a checked-in file already encodes the decision, cite it as the authority instead of restating its content.
- **Skill `model:` is turn-scoped, not skill-scoped**: an inline skill's `model:` override applies for the rest of the turn that invokes it, so composing such a skill mid-turn downgrades everything after it. Set `model:` only on `context: fork` skills or skills that always own the whole turn. For dispatcher skills, pass `model` per Agent call instead.
- **Skill `context: fork` caveats**: a fork gets no conversation history, so the body must open with an "invoking this skill IS the request" paragraph and take its input via args. Backgrounded forks run a narrower tool set (Agent may be missing, set `background: false` if needed), skill frontmatter hooks don't fire, and background-fork edits are outside `/rewind` checkpoints.
- **Testing local marketplace changes**: swap which source `hal-9000` resolves to: `claude plugin marketplace add /usr/local/hal-9000` before testing, `claude plugin marketplace add vinta/hal-9000` to switch back to the published version.
  - Adding a `hal-9000-local` entry with `"source": "directory"` to `extraKnownMarketplaces` DOES NOT work. A marketplace's identity comes from the `name` field inside `.claude-plugin/marketplace.json` (here, `"hal-9000"`), not the settings.json key, and Claude Code only ever registers one marketplace per name.
