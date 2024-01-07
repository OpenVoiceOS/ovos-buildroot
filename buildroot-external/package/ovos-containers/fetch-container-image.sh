#!/usr/bin/env bash

# Original script from Home Assistant

set -euo pipefail

# Variables
arch="$1"
image="$2"
dl_dir="$3"
dst_dir="$4"
image_name="docker.io/smartgic/${image}"
full_image_name="${image_name}:alpha"

# Fetch image digest
image_digest=$(skopeo --override-arch "${arch}" inspect --retry-times=5 "docker://${full_image_name}" | jq -r '.Digest')
if [ -z "${image_digest}" ]; then
	echo "Failed to fetch digest for ${full_image_name}"
	exit 1
fi

# Prepare file paths
image_file_name="${full_image_name//[:\/]/_}@${image_digest//[:\/]/_}"
image_file_path="${dl_dir}/${image_file_name}.tar"
dst_image_file_path="${dst_dir}/${image_file_name}.tar"
lock_file="${image_file_path}.lock"

# Function to fetch and copy image
fetch_and_copy_image() {
	if [ ! -f "${image_file_path}" ]; then
		echo "Fetching image: ${full_image_name} (digest ${image_digest})"
		skopeo --override-arch "${arch}" copy "docker://${image_name}@${image_digest}" "docker-archive:${image_file_path}:${full_image_name}"
	else
		echo "Skipping download of existing image: ${full_image_name} (digest ${image_digest})"
	fi

	cp "${image_file_path}" "${dst_image_file_path}"
}

# Main execution
{
	flock --verbose 3
	fetch_and_copy_image
} 3>"${lock_file}"
