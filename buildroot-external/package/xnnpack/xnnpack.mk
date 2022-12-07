################################################################################
#
# xnnpack
#
################################################################################

XNNPACK_VERSION = a50369c0fdd15f0f35b1a91c964644327a88d480
XNNPACK_SITE = $(call github,google,XNNPACK,$(XNNPACK_VERSION))

XNNPACK_LICENSE = BSD-2-Clause
XNNPACK_LICENSE_FILES = LICENSE

XNNPACK_DEPENDENCIES = clog cpuinfo pthreadpool fp16

XNNPACK_INSTALL_STAGING = YES
XNNPACK_SUPPORTS_IN_SOURCE_BUILD = NO

XNNPACK_CONF_OPTS = -DXNNPACK_BUILD_TESTS=OFF \
		    -DXNNPACK_BUILD_BENCHMARKS=OFF \
		    -DXNNPACK_USE_SYSTEM_LIBS=ON \
		    -DXNNPACK_USE_SYSTEM_LIBS=ON

$(eval $(cmake-package))
