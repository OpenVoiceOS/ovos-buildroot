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

cp -f ../buildroot-external/board/ovos/raspberrypi/cmdline.txt ${BINARIES_DIR}/rpi-firmware/cmdline.txt

# Copy the right config.txt file
for arg in "$@"
do
    case "${arg}" in
        --rpi3)
        cp -f ../buildroot-external/board/ovos/raspberrypi/rpi3/config.txt ${BINARIES_DIR}/rpi-firmware/config.txt
        ;;
        --rpi4)
        cp -f ../buildroot-external/board/ovos/raspberrypi/rpi4/config.txt ${BINARIES_DIR}/rpi-firmware/config.txt
        ;;
    esac
done
