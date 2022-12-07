################################################################################
#
# fp16
#
################################################################################

FP16_VERSION = 0a92994d729ff76a58f692d3028ca1b64b145d91
FP16_SITE = $(call github,Maratyszcza,FP16,$(FP16_VERSION))
FP16_LICENSE = BSD-2-Clause
FP16_LICENSE_FILES = LICENSE

FP16_SUPPORTS_IN_SOURCE_BUILD = NO
FP16_DEPENDENCIES = psimd

FP16_CONF_OPTS = -DCMAKE_SYSTEM_NAME=Linux \
		 -DCMAKE_SYSTEM_PROCESSOR=aarch64 \
		 -DFP16_BUILD_TESTS=OFF \
		 -DFP16_BUILD_BENCHMARKS=OFF

FP16_INSTALL_STAGING = YES
FP16_INSTALL_TARGET = NO

$(eval $(cmake-package))
