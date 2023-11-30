#!/usr/bin/env bash
set -e

build_dir=$1
dst_dir=$2

# shellcheck disable=SC2045
for image in $(ls -S ${build_dir}/images/*.tar); do
	podman --root "${dst_dir}" load --input "${image}"
done

