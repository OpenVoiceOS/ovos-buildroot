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
    echo "VARIANT=\"${OVOS_NAME} - Mycroft Edition\""
    echo "VARIANT_ID=${OVOS_ID}-${BOARD_ID}-mycroft"
} > "${TARGET_DIR}/usr/lib/os-release"

# Write machine-info
{
    echo "CHASSIS=${CHASSIS}"
    echo "DEPLOYMENT=${DEPLOYMENT}"
} > "${TARGET_DIR}/etc/machine-info"

cp -f ../buildroot-external/board/raspberrypi/config.txt ${BINARIES_DIR}/rpi-firmware/config.txt
cp -f ../buildroot-external/board/raspberrypi/cmdline.txt ${BINARIES_DIR}/rpi-firmware/cmdline.txt

cp -fr ../buildroot-external/rootfs-overlay/opt/mycroft/.skills-repo/.git* ${TARGET_DIR}/opt/mycroft/.skills-repo/
cp -fr ../buildroot-external/rootfs-overlay/opt/mycroft/skills/skill-balena-wifi-setup/.git* ${TARGET_DIR}/opt/mycroft/skills/skill-balena-wifi-setup/
cp -fr ../buildroot-external/rootfs-overlay/opt/mycroft/skills/skill-ovos-enclosure/.git* ${TARGET_DIR}/opt/mycroft/skills/skill-ovos-enclosure/
cp -fr ../buildroot-external/rootfs-overlay/opt/mycroft/skills/skill-ovos-mycroftgui/.git* ${TARGET_DIR}/opt/mycroft/skills/skill-ovos-mycroftgui/
cp -fr ../buildroot-external/rootfs-overlay/opt/mycroft/skills/skill-ovos-pairing/.git* ${TARGET_DIR}/opt/mycroft/skills/skill-ovos-pairing/
