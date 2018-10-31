#!/bin/bash
set -e

mount -t proc proc /proc
mount -t sysfs sys /sys
mount -t tmpfs tmp /run

mount /boot
mount / -o remount,rw

sed -i 's| init=/etc/init.d/init_resize.sh||' /boot/cmdline.txt
sync

DEVICE="/dev/mmcblk0"
PARTNR="p2"

CURRENTSIZEB=`fdisk -l $DEVICE$PARTNR | grep "Disk $DEVICE$PARTNR" | cut -d' ' -f5`
CURRENTSIZE=`expr $CURRENTSIZEB / 1024 / 1024`
MAXSIZEMB=`printf %s\\n 'unit MB print list' | parted | grep "Disk ${DEVICE}" | cut -d' ' -f3 | tr -d MB`

echo "[ok] applying resize operation.."
parted ${DEVICE} resizepart ${PARTNR} ${MAXSIZEMB}
echo "[done]"

partprobe $DEVICE

umount /boot
mount / -o remount,ro
sync

reboot
