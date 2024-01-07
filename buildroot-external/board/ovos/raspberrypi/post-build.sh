#!/bin/sh
set -eu

# Set board directory and include meta files
BOARD_DIR="$(dirname $0)"
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

# Function to handle Raspberry Pi specific files
handle_raspberry_pi() {
	local pi_version=$1
	echo "Handling Raspberry Pi ${pi_version} specific files"
	cp -f "../buildroot-external/board/ovos/raspberrypi/${pi_version}/config.txt" "${BINARIES_DIR}/rpi-firmware/config.txt"
	cp -f "../buildroot-external/board/ovos/raspberrypi/${pi_version}/RPI_EFI.fd" "${BINARIES_DIR}/rpi-firmware/RPI_EFI.fd"
	cp -f "../buildroot-external/board/ovos/raspberrypi/grub-efi.cfg" "${BINARIES_DIR}/efi-part/EFI/BOOT/grub.cfg"
	cp -f "../buildroot-external/board/ovos/raspberrypi/${pi_version}/sw-description" "${BINARIES_DIR}"
}

# Main function to execute script logic
main() {
	write_os_release
	write_machine_info

	echo "Copying cmdline.txt to ${BINARIES_DIR}/rpi-firmware/"
	cp -f ../buildroot-external/board/ovos/raspberrypi/cmdline.txt "${BINARIES_DIR}/rpi-firmware/cmdline.txt"

	echo "Creating grubenv"
	grub-editenv "${BINARIES_DIR}/efi-part/EFI/BOOT/grubenv" create

	echo "Checking for kernel in ${TARGET_DIR}"
	if [ -f "${TARGET_DIR}/boot/Image" ]; then
		echo "Found Image, renaming to kernel"
		mv "${TARGET_DIR}/boot/Image" "${TARGET_DIR}/boot/kernel"
	fi

	# Process command line arguments
	for arg in "$@"; do
		case "${arg}" in
			--rpi3) handle_raspberry_pi "rpi3" ;;
			--rpi4) handle_raspberry_pi "rpi4" ;;
			# --rpi5) handle_raspberry_pi "rpi5" ;;
		esac
	done

	# Prepare and sync home data
	local home_img="${BINARIES_DIR}/homefs.ext4"
	echo "Preparing home data at ${home_img}"
	rm -f "${home_img}"
	truncate --size="6890M" "${home_img}"
	mkfs.ext4 -L "homefs" -E lazy_itable_init=0,lazy_journal_init=0 "${home_img}"

	local home_mount_point="${BINARIES_DIR}/home"
	mkdir -p "${home_mount_point}"
	sudo mount -o loop,discard "${home_img}" "${home_mount_point}"
	sudo rsync -ah --progress "${TARGET_DIR}/home/"* "${home_mount_point}/"
	sudo umount "${home_img}"
}

main "$@"
