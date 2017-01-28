![HAL 9000](https://raw.githubusercontent.com/vinta/HAL-9000/master/assets/HAL_9000.jpg "HAL 9000")

# HAL 9000

[![](https://img.shields.io/badge/made%20with-%e2%9d%a4-ff69b4.svg?style=flat-square)](http://vinta.ws)

Dominating your dev environment like cats rule the Internet.

Building a Dockerized development environment with Ansible on macOS. Inspired by IFTTT's [Dash](https://github.com/IFTTT/dash).

HAL will configure these tools for you:

- Homebrew
- Ansible
- Docker for Mac with [NFS support](https://github.com/IFSight/d4m-nfs) (see [docker/for-mac#77](https://github.com/docker/for-mac/issues/77))
- Docker Compose
- Go
- Node.js
- Python
- dotfiles

## Prerequisite

First, you need to manually...

1. Install [Xcode](https://itunes.apple.com/us/app/xcode/id497799835)
2. Install Command Line Tools via `$ xcode-select --install`
3. Install [Docker for Mac](https://docs.docker.com/docker-for-mac/)
4. Unmount the `/Users` directory from [Docker for Mac Preferences](https://github.com/IFSight/d4m-nfs#d4m-nfs)

## Bootstrap

```bash
$ curl -L http://bit.ly/open-the-pod-bay-doors | bash
```

If you want to install only specific components (see [site.yml](https://github.com/vinta/HAL-9000/blob/master/playbooks/site.yml)):

```bash
$ curl -L http://bit.ly/open-the-pod-bay-doors | bash -s -- --tags docker
```

## Usage

```bash
# pull the repo and run ansible-playbook
$ hal update
$ hal update --tags docker,go

$ cd /path/to/your/project/ # that contains a docker-compose.yml file
$ hal up

# add the file to the dotfiles repository
$ hal link ~/.zshrc

# remove the file from the dotfiles repository
$ hal unlink ~/.zshrc

# force sync dotfiles
$ hal sync

# open the pod bay doors, please, HAL
$ hal open-the-pod-bay-doors
```
