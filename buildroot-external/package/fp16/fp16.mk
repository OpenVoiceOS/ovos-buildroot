################################################################################
#
# fp16
#
################################################################################

FP16_VERSION = 0a92994d729ff76a58f692d3028ca1b64b145d91
FP16_SITE = $(call github,Maratyszcza,FP16,$(FP16_VERSION))
FP16_LICENSE = MIT
FP16_LICENSE_FILES = LICENSE
FP16_INSTALL_STAGING = YES
# Only installs a header
FP16_INSTALL_TARGET = NO
FP16_DEPENDENCIES = psimd
FP16_CONF_OPTS = \
	-DFP16_BUILD_TESTS=OFF \
	-DFP16_BUILD_BENCHMARKS=OFF \
	-DPSIMD_SOURCE_DIR="$(PSIMD_DIR)"

$(eval $(cmake-package))
