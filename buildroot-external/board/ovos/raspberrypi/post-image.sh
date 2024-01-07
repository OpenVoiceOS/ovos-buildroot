#!/bin/bash

set -e

# Define board directory and related variables
BOARD_DIR="$(dirname "$0")"
BOARD_NAME="$(basename "${BOARD_DIR}")"
GENIMAGE_CFG="${BOARD_DIR}/genimage-${BOARD_NAME}.cfg"
GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"

# Define files for SWUPDATE
SWUPDATE_FILES=("sw-description" "rootfs.squashfs")

# Check if necessary files and directories exist
if [ ! -d "${BUILD_DIR}" ] || [ ! -f "${GENIMAGE_CFG}" ]; then
    echo "Required directories or config files are missing."
    exit 1
fi

# Function to create SWU file
create_swu_file() {
    local binaries_dir=$1
    shift
    local files=("$@")

    pushd "${binaries_dir}" > /dev/null
    printf '%s\n' "${files[@]}" | cpio -ov -H crc > rootfs.swu
    if [ $? -ne 0 ]; then
        echo "Error creating SWU file."
        exit 1
    fi
    popd > /dev/null
}

# Clean up function for EXIT trap
cleanup() {
    echo "Cleaning up temporary files."
    rm -rf "${ROOTPATH_TMP}"
    rm -rf "${GENIMAGE_TMP}"
}

# Setting up trap for cleanup on script exit
trap cleanup EXIT

# Create temporary root path
ROOTPATH_TMP="$(mktemp -d)"

# Generate image using genimage
echo "Generating image with genimage..."
genimage \
    --rootpath "${ROOTPATH_TMP}" \
    --tmppath "${GENIMAGE_TMP}" \
    --inputpath "${BINARIES_DIR}" \
    --outputpath "${BINARIES_DIR}" \
    --config "${GENIMAGE_CFG}"

if [ $? -ne 0 ]; then
    echo "Error during image generation."
    exit 1
fi

# Create SWU file
echo "Creating SWU file..."
create_swu_file "${BINARIES_DIR}" "${SWUPDATE_FILES[@]}"
