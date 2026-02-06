![HAL 9000](https://raw.githubusercontent.com/vinta/hal-9000/master/assets/hal-9000.jpg "HAL 9000")

# HAL 9000

[![](https://img.shields.io/badge/made%20with-%e2%9d%a4-ff69b4.svg?style=flat-square)](https://vinta.ws/code/)

Opinionated macOS development environment automation that dominates your dev setup like cats rule the Internet.

## Tech Stack

- [Claude Code](dotfiles/.claude)
- [Codex](dotfiles/.codex)
- [Gemini CLI](dotfiles/.gemini)
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

## Usage

```bash
# all you need is hal update
hal update

# if you only want to install specific components
hal update --tags python,node

# add the file to the dotfiles repository (creates symlink)
hal link ~/.zshrc

# copy the file to the dotfiles repository (preserves directory structure)
hal copy ~/.config/ghostty/

# backup the src to the dest
hal backup ~/.claude/projects "~/Dropbox/Apps/Claude Code/projects"

# force sync dotfiles and backups
hal sync

# open the pod bay doors, please, HAL
hal open-the-pod-bay-doors
```

## Development

```bash
# install dev dependencies and pre-commit hooks
make install

# after modifying bin/hal, regenerate zsh completion
make completion

# update local completion
hal sync
```

## Demo

<video src="https://github.com/user-attachments/assets/e86ead6d-189b-4361-a98b-4453ac0e8c25" width="800" height="450"></video>
