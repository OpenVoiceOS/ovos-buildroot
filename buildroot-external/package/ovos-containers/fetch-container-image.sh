#!/usr/bin/env bash
# Original script from Home Assistant

set -e
set -u
set -o pipefail

arch=$1
image=$2
dl_dir=$3
dst_dir=$4

image_name="docker.io/smartgic/${image}"
full_image_name="${image_name}:alpha"
image_digest=$(skopeo inspect --retry-times=5 "docker://${full_image_name}" | jq -r '.Digest')

image_file_name="${full_image_name//[:\/]/_}@${image_digest//[:\/]/_}"
image_file_path="${dl_dir}/${image_file_name}.tar"
dst_image_file_path="${dst_dir}/${image_file_name}.tar"

(
	# Use file locking to avoid race condition
	flock --verbose 3
	if [ ! -f "${image_file_path}" ]
	then
		echo "Fetching image: ${full_image_name} (digest ${image_digest})"
		skopeo copy "docker://${image_name}@${image_digest}" "docker-archive:${image_file_path}:${full_image_name}"
	else
		echo "Skipping download of existing image: ${full_image_name} (digest ${image_digest})"
	fi

	cp "${image_file_path}" "${dst_image_file_path}"
) 3>"${image_file_path}.lock"
