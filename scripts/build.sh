#!/bin/bash
set -e

mkdir -p release
mkdir -p logs

all_platforms=(rpi3)
for platform in "${all_platforms[@]}"; do
	make -C buildroot BR2_EXTERNAL=../buildroot-external distclean
	make -C buildroot BR2_EXTERNAL=../buildroot-external mycroftos_${platform}_defconfig

	# Optional if you need to change stuff, uncomment the next line.
#	make -C buildroot BR2_EXTERNAL=../buildroot-external menuconfig 

	make -C buildroot BR2_EXTERNAL=../buildroot-external 2>&1 | tee logs/buildroot_output.txt
	cp -f buildroot/output/images/sdcard.img release/MycroftOS_${platform}.img
done
