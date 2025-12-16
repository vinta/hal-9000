![HAL 9000](https://raw.githubusercontent.com/vinta/hal-9000/master/assets/HAL_9000.jpg "HAL 9000")

# HAL 9000

[![Run in Smithery](https://smithery.ai/badge/skills/vinta)](https://smithery.ai/skills?ns=vinta&utm_source=github&utm_medium=badge)


[![](https://img.shields.io/badge/made%20with-%e2%9d%a4-ff69b4.svg?style=flat-square)](https://vinta.ws/code/)

Automatically setup a productive development environment with Ansible on macOS.

Dominating your dev environment like cats rule the Internet.

## Development Stack

- [Python](playbooks/roles/python/tasks/main.yml)
- [Node.js](playbooks/roles/node/tasks/main.yml)
- [Solidity](playbooks/roles/solidity/tasks/main.yml)
- [Docker](playbooks/roles/docker/tasks/main.yml)
- [Kubernetes](playbooks/roles/kubernetes/tasks/main.yml)
- [Amazon Web Services](playbooks/roles/aws/tasks/main.yml)
- [Google Cloud](playbooks/roles/gcp/tasks/main.yml)

## Bootstrap

```bash
curl -L https://raw.githubusercontent.com/vinta/hal-9000/master/bin/open-the-pod-bay-doors | bash
```

## Usage

```bash
# pull the repo and run ansible-playbook
hal update
hal update --tags docker,kubernetes

# add the file to the dotfiles repository (creates symlink)
hal link ~/.zshrc

# copy the file to the dotfiles repository (preserves directory structure)
hal copy ~/.config/some-app/config.toml

# force sync dotfiles
hal sync

# open the pod bay doors, please, HAL
hal open-the-pod-bay-doors
```

## Development

After modifying hal functions, regenerate the zsh completion script:

```bash
python scripts/generate-completion.py

# update local completion
hal sync
```
