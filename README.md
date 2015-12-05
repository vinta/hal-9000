![HAL 9000](https://raw.githubusercontent.com/vinta/HAL-9000/master/assets/HAL_9000.jpg "HAL 9000")

# HAL 9000

[![](https://img.shields.io/badge/made%20with-%e2%9d%a4-ff69b4.svg?style=flat-square)](http://vinta.ws)

Build Dockerized development environments with Ansible on Mac OS X. Inspired by IFTTT's [Dash](https://github.com/IFTTT/dash).

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

# add the file to the dotfiles repository
$ hal unlink ~/.zshrc

# force sync dotfiles
$ hal sync

# open the pod bay doors, please, Hal
$ hal open-the-pod-bay-doors
```
