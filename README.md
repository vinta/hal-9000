# HAL 9000

![HAL 9000](https://raw.githubusercontent.com/vinta/hal-9000/main/assets/hal-9000.jpg "HAL 9000")

Opinionated AI coding agent and dev environment automation for macOS that dominates your dev setup like cats rule the Internet.

> This project is named after Arthur C. Clarke's 2001: A Space Odyssey, a heuristic algorithmic computer designed for sentient processing and total mission control.

## Bootstrap

All-in-one command to set up:

- [Agent Skills](skills)
- [Claude Code](dotfiles/.claude) / [Plugins](plugins) / [Rules](dotfiles/.claude/rules) / [Output Styles](dotfiles/.claude/output-styles) / [Statusline](plugins/hal-statusline)
- [Codex](dotfiles/.codex)
- [Python](playbooks/roles/python/tasks/main.yml)
- [Node.js](playbooks/roles/node/tasks/main.yml)
- [Bun](playbooks/roles/bun/tasks/main.yml)
- [Solidity](playbooks/roles/solidity/tasks/main.yml)
- [Docker](playbooks/roles/docker/tasks/main.yml) (OrbStack)
- [Kubernetes](playbooks/roles/kubernetes/tasks/main.yml)
- [Amazon Web Services](playbooks/roles/aws/tasks/main.yml)
- [Google Cloud](playbooks/roles/gcp/tasks/main.yml)

```bash
curl -sL https://raw.githubusercontent.com/vinta/hal-9000/main/bin/open-the-pod-bay-doors.sh | bash
```

## Components

### Dotfiles

Tool configs hardened against supply chain attacks and tuned for better DX:

- [`.claude/settings.json`](dotfiles/.claude/settings.json)
- [`.codex/config.toml`](dotfiles/.codex/config.toml)
- [`.config/ghostty/config`](dotfiles/.config/ghostty/config)
- [`.config/uv/uv.toml`](dotfiles/.config/uv/uv.toml)
- [`.npmrc`](dotfiles/.npmrc)
- [`.zshrc`](dotfiles/.zshrc)

### CLAUDE.md / AGENTS.md

Dogmatic yet meticulously crafted global instructions for agentic coding:

- [`~/.claude/CLAUDE.md`](dotfiles/.claude/CLAUDE.md)
- [`~/.codex/AGENTS.md`](dotfiles/.codex/AGENTS.md)

Also see:

- [Claude Code: Things I Learned After Using It Every Day](https://vinta.ws/code/claude-code-useful-plugins-skills-and-mcps.html)

### Skills

Agentic skills sharpened by daily use:

- [commit](skills/commit/SKILL.md): Splits your changes into atomic conventional commits, hunk by hunk if needed
- [fuck-over-engineering](skills/fuck-over-engineering/SKILL.md): Ranks what to cut in your codebase, deletes only what you pick
- [best-practices](skills/best-practices/SKILL.md): Searches the web for the recommended way and common gotchas
- [blindspot](skills/blindspot/SKILL.md): Interviews you to turn unknown unknowns into questions you can prompt with
- [simple-english](skills/simple-english/SKILL.md): Rewrites text in Global English: plain words, still native-sounding
- [write-like-me](skills/write-like-me/SKILL.md): Drafts or rewrites English prose in my own voice at native fluency
- [audit-claude-settings](skills/audit-claude-settings/SKILL.md): Audits your Claude Code settings against the latest docs
- [refactor-claude-md](skills/refactor-claude-md/SKILL.md): Refactors a CLAUDE.md so every line earns its always-loaded cost
- [refactor-agents-md](skills/refactor-agents-md/SKILL.md): Refactors an AGENTS.md the same way, for Codex
- [refactor-memory](skills/refactor-memory/SKILL.md): Prunes stale Claude Code auto memory and regroups the MEMORY.md index
- [refactor-skill](skills/refactor-skill/SKILL.md): Refactors a skill by simplifying it instead of complicating it

```bash
/plugin marketplace add vinta/hal-9000
/plugin install hal-skills@hal-9000
```

If you want to use them in Codex or other coding agents:

```bash
npx skills add vinta/hal-9000
```

### Claude Code Plugins

Plugins that wire their own hooks and run themselves:

- [hal-session-auto-rename](plugins/hal-session-auto-rename): Automatically name each session and rename it as the conversation evolves
- [hal-voice](plugins/hal-voice): Play HAL 9000 voice clips on Claude Code hook events

```bash
/plugin marketplace add vinta/hal-9000
/plugin install hal-session-auto-rename@hal-9000
/plugin install hal-voice@hal-9000
```

### Claude Code Statusline

- [hal-statusline](plugins/hal-statusline): Show the current model, directory, git branch, and model usage status in [statusline](https://code.claude.com/docs/en/statusline)
  - Plus **a grammar check on every prompt you type**, with explanations in Traditional Chinese

```bash
curl -sL https://raw.githubusercontent.com/vinta/hal-9000/main/scripts/install-hal-statusline.sh | bash
```

### CLI: `hal`

```bash
hal update                            # Run all Ansible roles to set up the dev environment
hal update --tags python,node         # Run specific Ansible roles
hal link ~/.zshrc                     # Move file into dotfiles/ and symlink it back
hal unlink ~/.zshrc                   # Move file back from dotfiles/ and remove the symlink
hal sync                              # Sync all links
hal backup                            # Back up live data to Dropbox
hal restore                           # Restore live data from Dropbox (overwrites local)
hal open-the-pod-bay-doors            # Open the pod bay doors, please, HAL
```

## Development

```bash
make install                          # Install dev dependencies and pre-commit hooks
make test                             # Run tests
make hal-completion                   # Regenerate zsh completion after modifying bin/hal.py
hal sync                              # Update local completion
```

## Demo

<video src="https://github.com/user-attachments/assets/e86ead6d-189b-4361-a98b-4453ac0e8c25" width="800" height="450"></video>
