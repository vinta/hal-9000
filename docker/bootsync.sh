#!/bin/sh

sudo umount /Users
sudo /usr/local/etc/init.d/nfs-client start
sleep 1
sudo mount.nfs 192.168.99.1:/Users /Users -v -o rw,async,noatime,rsize=32768,wsize=32768,proto=udp,udp,nfsvers=3

echo -e "nameserver 8.8.8.8\nnameserver 8.8.4.4" | sudo tee /etc/resolv.conf
