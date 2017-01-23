#!/bin/bash

# https://github.com/docker/for-mac/issues/668
# You must be on Docker 1.12.2-rc1-beta27 or greater

cd ~/Library/Containers/com.docker.docker/Data/database/
filename="com.docker.driver.amd64-linux/disk/full-sync-on-flush"
git reset --hard
cat $filename
echo "false" > $filename
git add $filename && git commit -s -m "Disable flushing"
echo "You should now restart Docker for Mac"
