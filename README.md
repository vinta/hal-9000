# HAL 9000

![HAL 9000](https://raw.githubusercontent.com/vinta/hal-9000/main/assets/hal-9000.jpg "HAL 9000")

Opinionated macOS development environment automation that dominates your dev setup like cats rule the Internet.

> This project is named after Arthur C. Clarke's 2001: A Space Odyssey, a heuristic algorithmic computer designed for sentient processing and total mission control.

## Bootstrap

All-in-one command to set up:

- [Agent Skills](plugins/hal-skills)
- [Claude Code](dotfiles/.claude) / [Plugins](plugins) / [Rules](dotfiles/.claude/rules) / [Statusline](plugins/hal-statusline)
- [Codex](dotfiles/.codex)
- [Gemini](dotfiles/.gemini)
- [Python](playbooks/roles/python/tasks/main.yml)
- [Node.js](playbooks/roles/node/tasks/main.yml)
- [Bun](playbooks/roles/bun/tasks/main.yml)
- [Solidity](playbooks/roles/solidity/tasks/main.yml)
- [Docker](playbooks/roles/docker/tasks/main.yml) (OrbStack)
- [Kubernetes](playbooks/roles/kubernetes/tasks/main.yml)
- [Amazon Web Services](playbooks/roles/aws/tasks/main.yml)
- [Google Cloud](playbooks/roles/gcp/tasks/main.yml)

```bash
curl -sL https://raw.githubusercontent.com/vinta/hal-9000/main/bin/open-the-pod-bay-doors | bash
```

## Components

If you prefer only using some of them:

### Claude Code Plugin: `hal-skills`

- [magi](plugins/hal-skills/skills/magi): Three-agent brainstorming panel for competing perspectives
- [magi-ex](plugins/hal-skills/skills/magi-ex): Multi-model (Claude/Codex/Gemini) brainstorming panel for competing perspectives
- [second-opinions](plugins/hal-skills/skills/second-opinions): Parallel review from multiple external models
- [commit](plugins/hal-skills/skills/commit): Creates clean, atomic git commits
- [update-allowed-tools](plugins/hal-skills/skills/update-allowed-tools): Updates skill allowed-tools frontmatter

```bash
claude plugin marketplace add vinta/hal-9000
claude plugin install hal-skills@hal-9000
```

If you want to use them in Codex or Gemini CLI:

```bash
npx skills add vinta/hal-9000
```

### Claude Code Plugin: `hal-voice`

- [hal-voice](plugins/hal-voice): Play HAL 9000 voice clips on Claude Code hook events

```bash
claude plugin marketplace add vinta/hal-9000
claude plugin install hal-voice@hal-9000
```

### Claude Code Statusline

- [hal-statusline](plugins/hal-statusline): Show the current model, directory, and git branch in [statusline](https://code.claude.com/docs/en/statusline). Plus **a grammar check on every prompt you type**, with explanations in Traditional Chinese

```bash
curl -sL https://raw.githubusercontent.com/vinta/hal-9000/main/scripts/install-hal-statusline.sh | bash
```

### CLI: `hal`

```bash
hal update                            # Run all Ansible roles to set up the dev environment
hal update --tags python,node         # Run specific Ansible roles
hal link ~/.zshrc                     # Move file into dotfiles/ and symlink it back
hal copy ~/.config/ghostty/config     # Copy file into dotfiles/ (no symlink)
hal sync                              # Sync all links and copies
hal open-the-pod-bay-doors            # Open the pod bay doors, please, HAL
```

## Development

```bash
make install                          # Install dev dependencies and pre-commit hooks
make test                             # Run tests
make hal-completion                   # Regenerate zsh completion after modifying bin/hal
hal sync                              # Update local completion
```

## Demo

<video src="https://github.com/user-attachments/assets/e86ead6d-189b-4361-a98b-4453ac0e8c25" width="800" height="450"></video>
