#!/bin/bash
# -*- mode: shell-script; indent-tabs-mode: nil; sh-basic-offset: 4; -*-
# ex: ts=8 sw=4 sts=4 et filetype=sh

check() {
	require_binaries cat || return 1
	require_binaries cut || return 1
	require_binaries switch_root || return 1
	require_binaries cmp || return 1
	require_binaries expr || return 1
	require_binaries echo || return 1
	require_binaries grep || return 1
	require_binaries mkdir || return 1
	require_binaries mount || return 1
	require_binaries umount || return 1
	require_binaries modprobe || return 1
	require_binaries sleep || return 1
	require_binaries rm || return 1
	return 0
}

depends() {
    return 0
}

installkernel() {
    return 0
}

install() {

    inst_multiple mount umount cat cut cmp grep mkdir expr switch_root echo sleep rm
    cp $moddir/init-readonly-rootfs-overlay-boot.sh $initdir/init
}
