![HAL 9000](https://raw.githubusercontent.com/vinta/HAL-9000/master/assets/HAL_9000.jpg "HAL 9000")

# HAL 9000

[![](https://img.shields.io/badge/made%20with-%e2%9d%a4-ff69b4.svg?style=flat-square)](https://vinta.ws/code/)

Automatically setup a productive development environment with Ansible on macOS.

Dominating your dev environment like cats rule the Internet.

## Toolkit

- [Python](https://github.com/vinta/HAL-9000/blob/master/playbooks/roles/python/tasks/main.yml)
- [Node.js](https://github.com/vinta/HAL-9000/blob/master/playbooks/roles/node/tasks/main.yml)
- [Go](https://github.com/vinta/HAL-9000/blob/master/playbooks/roles/go/tasks/main.yml)
- [Docker](https://github.com/vinta/HAL-9000/blob/master/playbooks/roles/docker/tasks/main.yml)
- [Kubernetes](https://github.com/vinta/HAL-9000/blob/master/playbooks/roles/kubernetes/tasks/main.yml)
- [Ethereum](https://github.com/vinta/HAL-9000/blob/master/playbooks/roles/ethereum/tasks/main.yml)
- [Apache Spark](https://github.com/vinta/HAL-9000/blob/master/playbooks/roles/spark/tasks/main.yml)
- [Amazon Web Services](https://github.com/vinta/HAL-9000/blob/master/playbooks/roles/aws/tasks/main.yml)
- [Google Cloud](https://github.com/vinta/HAL-9000/blob/master/playbooks/roles/gcp/tasks/main.yml)

## Prerequisite

First, you need to manually:

1. Install Command Line Tools via `xcode-select --install`
2. Install [Docker Desktop on Mac](https://docs.docker.com/docker-for-mac/install/)

## Bootstrap

```bash
curl -L https://bit.ly/open-the-pod-bay-doors | bash
```

## Usage

```bash
# pull the repo and run ansible-playbook
hal update
hal update --tags docker,kubernetes

# add the file to the dotfiles repository
hal link ~/.zshrc

# remove the file from the dotfiles repository
hal unlink ~/.zshrc

# force sync dotfiles
hal sync

# open the pod bay doors, please, HAL
hal open-the-pod-bay-doors
```
