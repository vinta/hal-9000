---
paths:
  - "skills/**"
  - "plugins/**"
  - "dotfiles/.claude/**"
  - ".claude/**"
---

# Claude Code Development Rules

- Claude Code moves fast and its docs change under you. Before modifying anything Claude Code related (settings, rules, skills, plugins, marketplaces), fetch the latest docs first: use the per-topic URLs under "Documentation Links" in CLAUDE.md, or discover other pages via the index at https://code.claude.com/docs/llms.txt.
- All skill descriptions must start with `Use when` (may have a `(project)` prefix if it's a project-level skill).
- **Testing local marketplace changes**: swap which source `hal-9000` resolves to: `claude plugin marketplace add /usr/local/hal-9000` before testing, `claude plugin marketplace add vinta/hal-9000` to switch back to the published version.
  - Adding a `hal-9000-local` entry with `"source": "directory"` to `extraKnownMarketplaces` DOES NOT work. A marketplace's identity comes from the `name` field inside `.claude-plugin/marketplace.json` (here, `"hal-9000"`), not the settings.json key, and Claude Code only ever registers one marketplace per name.
