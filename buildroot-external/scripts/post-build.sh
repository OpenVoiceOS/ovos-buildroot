#!/bin/sh

set -eu

# Define board directory and related variables
BOARD_DIR=$2
BOARD_TYPE=$(basename "${BOARD_DIR}")

# Source external metadata
. "${BR2_EXTERNAL_OPENVOICEOS_PATH}/meta"
. "${BOARD_DIR}/meta"

# Function to create and write os-release file
write_os_release() {
    local os_release_file="${TARGET_DIR}/usr/lib/os-release"
    echo "Creating os-release at ${os_release_file}"
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
    } > "${os_release_file}"
}

# Function to create and write machine-info file
write_machine_info() {
    local machine_info_file="${TARGET_DIR}/etc/machine-info"
    echo "Creating machine-info at ${machine_info_file}"
    {
        echo "CHASSIS=${CHASSIS}"
        echo "DEPLOYMENT=${DEPLOYMENT}"
    } > "${machine_info_file}"
}

# Function to copy files based on board type
copy_board_specific_files() {
    echo "Copying files for board type: ${BOARD_TYPE}"

    case "${BOARD_TYPE}" in
        "rpi3"|"rpi4"|"rpi5")
            cp -f "${BOARD_DIR}/../cmdline.txt" "${BINARIES_DIR}/rpi-firmware/cmdline.txt"
            cp -f "${BOARD_DIR}/config.txt" "${BINARIES_DIR}/rpi-firmware/config.txt"
            cp -f "${BOARD_DIR}/RPI_EFI.fd" "${BINARIES_DIR}/rpi-firmware/RPI_EFI.fd"
            cp -f "${BOARD_DIR}/../grub-efi.cfg" "${BINARIES_DIR}/efi-part/EFI/BOOT/grub.cfg"
            cp -f "${BOARD_DIR}/sw-description" "${BINARIES_DIR}"
            ;;
        "ova"|"pc")
            cp -f "${BOARD_DIR}/grub-efi.cfg" "${BINARIES_DIR}/efi-part/EFI/BOOT/grub.cfg"
            cp -f "${BOARD_DIR}/cmdline.txt" "${BINARIES_DIR}"
            cp -f "${BOARD_DIR}/sw-description" "${BINARIES_DIR}"
            ;;
        *)
            echo "No specific files to copy for board type: ${BOARD_TYPE}"
            ;;
    esac
}

# Function to handle kernel renaming based on board type
handle_kernel_renaming() {
    case "${BOARD_TYPE}" in
        "rpi3"|"rpi4"|"rpi5")
            grub-editenv "${BINARIES_DIR}/efi-part/EFI/BOOT/grubenv" create
            if [ -f "${TARGET_DIR}/boot/Image" ]; then
                echo "Found Image, renaming to kernel"
                mv "${TARGET_DIR}/boot/Image" "${TARGET_DIR}/boot/kernel"
            fi
            ;;
        "ova"|"pc")
            grub-editenv "${BINARIES_DIR}/efi-part/EFI/BOOT/grubenv" create
            if [ -f "${TARGET_DIR}/boot/bzImage" ]; then
                echo "Found bzImage, renaming to kernel"
                mv "${TARGET_DIR}/boot/bzImage" "${TARGET_DIR}/boot/kernel"
            fi
            ;;
        *)
            echo "No kernel renaming logic needed for board type: ${BOARD_TYPE}"
            ;;
    esac
}

# Main function to execute script logic
main() {
    write_os_release
    write_machine_info
    copy_board_specific_files
    handle_kernel_renaming

    # Prepare and sync home data
    local home_img="${BINARIES_DIR}/homefs.ext4"
    echo "Preparing home data at ${home_img}"
    rm -f "${home_img}"
    truncate --size="6890M" "${home_img}"
    mkfs.ext4 -L "homefs" -E lazy_itable_init=0,lazy_journal_init=0 "${home_img}"

    local home_mount_point="${BINARIES_DIR}/home"
    mkdir -p "${home_mount_point}"
    sudo mount -o loop,discard "${home_img}" "${home_mount_point}"
    sudo rsync -avPHSX "${TARGET_DIR}/home/"* "${home_mount_point}/"
    sudo umount "${home_img}"
}

# Ensure the script is called with the correct number of arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <build_dir> <board_dir>"
    exit 1
fi

# Call the main function
main
