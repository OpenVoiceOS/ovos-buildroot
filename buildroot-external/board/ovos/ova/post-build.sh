#!/bin/sh

set -u
set -e

BOARD_DIR="$(dirname $0)"

. "${BR2_EXTERNAL_OPENVOICEOS_PATH}/meta"
. "${BOARD_DIR}/meta"

# Write os-release
{
    echo "NAME=\"${OVOS_NAME}\""
    echo "VERSION=\"${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_BUILD} ${BOARD_NAME}\""
    echo "ID=${OVOS_ID}"
    echo "VERSION_ID=${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_BUILD}"
    echo "PRETTY_NAME=\"${OVOS_NAME} ${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_BUILD} ${BOARD_NAME}\""
    echo "CPE_NAME=cpe:2.3:o:openvoiceos:${OVOS_ID}:${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_BUILD}:*:${DEPLOYMENT}:*:*:*:${BOARD_ID}:*"
    echo "HOME_URL=https://github.com/OpenVoiceOS/OpenVoiceOS"
    echo "DOCUMENTATION_URL=https://github.com/OpenVoiceOS/OpenVoiceOS/tree/develop/documentation"
    echo "SUPPORT_URL=https://github.com/OpenVoiceOS/OpenVoiceOS/issues"
    echo "VARIANT=\"${OVOS_NAME} - Buildroot Edition\""
    echo "VARIANT_ID=${OVOS_ID}-${BOARD_ID}-buildroot"
} > "${TARGET_DIR}/usr/lib/os-release"

# Write machine-info
{
    echo "CHASSIS=${CHASSIS}"
    echo "DEPLOYMENT=${DEPLOYMENT}"
} > "${TARGET_DIR}/etc/machine-info"

cp -f ../buildroot-external/board/ovos/ova/grub-efi.cfg ${BINARIES_DIR}/efi-part/EFI/BOOT/grub.cfg
cp -f ../buildroot-external/board/ovos/ova/cmdline.txt ${BINARIES_DIR}
cp -f ../buildroot-external/board/ovos/ova/sw-description ${BINARIES_DIR}

grub-editenv "${BINARIES_DIR}/efi-part/EFI/BOOT/grubenv" create

echo "Check for compressed kernel in ${TARGET_DIR}"
if [ -f "${TARGET_DIR}/boot/bzImage" ]; then
    echo "Found bzImage, renaming to kernel"
    mv ${TARGET_DIR}/boot/bzImage ${TARGET_DIR}/boot/kernel
fi

# Prepare home data
rm -f ${BINARIES_DIR}/homefs.ext4
truncate --size="6890M" ${BINARIES_DIR}/homefs.ext4
mkfs.ext4 -L "homefs" -E lazy_itable_init=0,lazy_journal_init=0 ${BINARIES_DIR}/homefs.ext4

# Mount home image
mkdir -p ${BINARIES_DIR}/home
sudo mount -o loop,discard ${BINARIES_DIR}/homefs.ext4 ${BINARIES_DIR}/home

# sync home folder
sudo rsync -ah --progress ${TARGET_DIR}/home/* ${BINARIES_DIR}/home/

# Unmount home image
sudo umount ${BINARIES_DIR}/homefs.ext4
