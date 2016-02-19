#!/bin/sh

sudo umount /Users
sudo mkdir -p /Users
sudo /usr/local/etc/init.d/nfs-client start
sudo mount -t nfs -o nolock,vers=3,udp,noatime,actimeo=1 192.168.99.1:/Users /Users
