![HAL 9000](https://raw.githubusercontent.com/vinta/HAL-9000/master/assets/HAL_9000.jpg "HAL 9000")

# HAL 9000

[![](https://img.shields.io/badge/made%20with-%e2%9d%a4-ff69b4.svg?style=flat-square)](http://vinta.ws)

Dominating your dev environment like cats rule the Internet.

Building a Dockerized development environment with Ansible on Mac OS X. Inspired by IFTTT's [Dash](https://github.com/IFTTT/dash).

HAL will configure these tools for you, Dave:

- Homebrew
- Ansible
- VirtualBox
- Docker
- Docker Machine
- Docker Compose
- Go
- Node.js
- Python
- and your dotfiles

You may need to...

1. Install [Xcode](https://itunes.apple.com/us/app/xcode/id497799835) from Mac App Store
2. Install Command Line Tools via `xcode-select --install`

## Bootstrap

``` bash
$ bash <(curl -fsSL https://raw.githubusercontent.com/vinta/HAL-9000/master/bin/open-the-pod-bay-doors)
```

## Usage

``` bash
# pull the repo and run ansible-playbook
$ hal update

# create the Docker Machine VM
$ hal create

# setup nginx-proxy and dnsmasq
$ hal prepare

$ cd /path/to/your_project/ # that contains a docker-compose.yml file
$ docker-compose up
# or
$ hal up # == hal prepare + docker-compose up

# add the file to the dotfiles repository
$ hal link ~/.zshrc

# remove the file from the dotfiles repository
$ hal unlink ~/.zshrc

# force sync dotfiles
$ hal sync

# open the pod bay doors, please, HAL
$ hal open-the-pod-bay-doors
```

## Extras

``` bash
# it's optional to setup port forwarding to access Docker containers via 127.0.0.1
$ VBoxManage modifyvm "eva01" --natpf1 "Rule 8000,tcp,,8000,,8000" && \
  VBoxManage modifyvm "eva01" --natpf1 "Rule 8001,tcp,,8001,,8001" && \
  VBoxManage modifyvm "eva01" --natpf1 "Rule 8002,tcp,,8002,,8002" && \
  VBoxManage modifyvm "eva01" --natpf1 "Rule 8003,tcp,,8003,,8003"
```
