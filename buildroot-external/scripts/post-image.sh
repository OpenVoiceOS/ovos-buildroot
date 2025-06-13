#!/bin/bash

set -eu

# Define board directory and related variables
BOARD_DIR=$2
BOARD_TYPE="$(basename "${BOARD_DIR}")"
GENIMAGE_CFG="${BOARD_DIR}/genimage-${BOARD_TYPE}.cfg"
GENIMAGE_TMP="${BUILD_DIR}/genimage.tmp"

# Clean up function for EXIT trap
cleanup() {
    echo "Cleaning up temporary files."
    rm -rf "${ROOTPATH_TMP}" "${GENIMAGE_TMP}"
}

# Main function to execute script logic
main() {
    # Check if necessary files and directories exist
    if [ ! -d "${BUILD_DIR}" ] || [ ! -f "${GENIMAGE_CFG}" ]; then
        echo "Required directories or config files are missing."
        exit 1
    fi

    # Generate image using genimage
    echo "Generating image with genimage..."
    if ! genimage \
        --rootpath "${ROOTPATH_TMP}" \
        --tmppath "${GENIMAGE_TMP}" \
        --inputpath "${BINARIES_DIR}" \
        --outputpath "${BINARIES_DIR}" \
        --config "${GENIMAGE_CFG}"; then
        echo "Error during image generation."
        exit 1
    fi

}

# Setting up trap for cleanup on script exit
trap cleanup EXIT

# Check for correct number of arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <build_dir> <board_dir>"
    exit 1
fi

# Create temporary root path
ROOTPATH_TMP="$(mktemp -d)"

# Call the main function
main
