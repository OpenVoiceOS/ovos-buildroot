#!/bin/bash
# -*- mode: shell-script; indent-tabs-mode: nil; sh-basic-offset: 4; -*-
# ex: ts=8 sw=4 sts=4 et filetype=sh

check() {
	require_binaries busybox || return 1
	require_binaries cat || return 1
	require_binaries switch_root || return 1
	require_binaries cmp || return 1
	require_binaries expr || return 1
	require_binaries grep || return 1
	require_binaries mkdir || return 1
	require_binaries mount || return 1
	require_binaries modprobe || return 1
	require_binaries log || return 1
	return 0
}

depends() {
    return 0
}

installkernel() {
    return 0
}

install_busybox_links() {
	dir="${1}"
	linkname="${2}"

	(cd "${dracutsysrootdir?}${dir}" &&
	for x in *; do
		if [ "$(readlink "${x}")" = "${linkname}" ]; then
			ln -sf "${linkname}" "${initdir?}/${dir}/${x}"
		fi
	done
	)
}

install() {

        inst_multiple mount umount cat cmp grep mkdir expr chroot

        # Install busybox binary
        inst_multiple /bin/busybox
        if [ -e "${dracutsysrootdir?}/lib64" ]; then
                ln -sf lib "${initdir?}/lib64"
                ln -sf lib "${initdir?}/usr/lib64"
        fi

        if [ -e "${dracutsysrootdir?}/lib32" ]; then
                ln -sf lib "${initdir?}/lib32"
                ln -sf lib "${initdir?}/usr/lib32"
        fi

        install_busybox_links "/bin" "busybox"
        install_busybox_links "/sbin" "../bin/busybox"
        if [ ! -L "${dracutsysrootdir?}/bin" ]; then
                install_busybox_links "/usr/bin" "../../bin/busybox"
                install_busybox_links "/usr/sbin" "../../bin/busybox"
        fi

    # inst does not work for some reason. Use cp(1) instead.
    #inst "$moddir/init-readonly-rootfs-overlay-boot.sh" "/init"
    cp $moddir/init-readonly-rootfs-overlay-boot.sh $initdir/init
}
