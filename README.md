# HAL 9000

![HAL 9000](https://raw.githubusercontent.com/vinta/hal-9000/master/assets/hal-9000.jpg "HAL 9000")

Opinionated macOS development environment automation that dominates your dev setup like cats rule the Internet.

> This project is named after Arthur C. Clarke's 2001: A Space Odyssey, a heuristic algorithmic computer designed for sentient processing and total mission control.

## Tech Stack

- [Agent Skills](skills)
- [Claude Code](dotfiles/.claude) / [Plugins](plugins)
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

## Bootstrap

```bash
curl -L https://raw.githubusercontent.com/vinta/hal-9000/master/bin/open-the-pod-bay-doors | bash
```

## Components

### CLI: `hal`

```bash
hal update                      # Run Ansible playbook to set up the dev environment
hal update --tags python,node   # Run specific Ansible roles

hal link ~/.zshrc               # Move file into dotfiles/ and symlink it back
hal copy ~/.config/ghostty/     # Copy file into dotfiles/ (no symlink)
hal sync                        # Sync all links and copies

hal open-the-pod-bay-doors      # Open the pod bay doors, please, HAL
```

### Agent Skills

- [magi](skills/magi): Three-agent deliberation system for competing perspectives
- [second-opinions](skills/second-opinions): Parallel review from multiple external models
- [commit](skills/commit): Creates clean, atomic git commits
- [explore-codebase](skills/explore-codebase): Searches codebase with ast-grep, ripgrep, and fd
- [update-allowed-tools](skills/update-allowed-tools): Updates skill allowed-tools frontmatter

```bash
npx skills add vinta/hal-9000
```

### Claude Code Plugins

- [hal-voice](plugins/hal-voice): HAL 9000 voice clips on Claude Code hook events

```bash
claude plugin marketplace add vinta/hal-9000
claude plugin install hal-voice@hal-9000
```

## Development

```bash
make install          # Install dev dependencies and pre-commit hooks
make hal-completion   # Regenerate zsh completion after modifying bin/hal
hal sync              # Update local completion
```

## Demo

<video src="https://github.com/user-attachments/assets/e86ead6d-189b-4361-a98b-4453ac0e8c25" width="800" height="450"></video>
