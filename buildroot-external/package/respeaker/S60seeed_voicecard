#!/bin/sh
#
# Configure seeed-voicecard....
#

echo "Starting seeed-voicecard..."
mount -t configfs none /sys/kernel/config
mkdir -p /boot
mount -t vfat /dev/mmcblk0p1 /boot
/usr/bin/seeed-voicecard
touch /var/lock/seeed-voicecard
