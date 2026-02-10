# HAL 9000

![HAL 9000](https://raw.githubusercontent.com/vinta/hal-9000/master/assets/hal-9000.jpg "HAL 9000")

Opinionated macOS development environment automation that dominates your dev setup like cats rule the Internet.

> This project is named after Arthur C. Clarke's 2001: A Space Odyssey, a heuristic algorithmic computer designed for sentient processing and total mission control.

## Tech Stack

- [Agent Skills](skills)
- [Claude Code](dotfiles/.claude)
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

## Usage

All you need is one command:

```bash
hal update
```

If you only want to install specific components:

```bash
hal update --tags python,node
```

Move file into dotfiles/ and symlink it back:

```bash
hal link ~/.zshrc
```

Copy file into dotfiles/ (no symlink):

```bash
hal copy ~/.config/ghostty/
```

Sync all links and copies:

```bash
hal sync
```

Open the pod bay doors, please, HAL:

```bash
hal open-the-pod-bay-doors
```

## Skills

If you only need agent skills:

```bash
npx skills add vinta/hal-9000
```

## Development

Install dev dependencies and pre-commit hooks:

```bash
make install
```

After modifying `./bin/hal`, regenerate zsh completion:

```bash
make hal-completion
```

Update local completion:

```bash
hal sync
```

## Demo

<video src="https://github.com/user-attachments/assets/e86ead6d-189b-4361-a98b-4453ac0e8c25" width="800" height="450"></video>
