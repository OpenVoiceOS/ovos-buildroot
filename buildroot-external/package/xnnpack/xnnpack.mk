################################################################################
#
# xnnpack
#
################################################################################

XNNPACK_VERSION = e4b2b942b4a6d84b680ed690fee42ae99865945c
XNNPACK_SITE = $(call github,google,XNNPACK,$(XNNPACK_VERSION))
XNNPACK_LICENSE = BSD-3-Clause
XNNPACK_LICENSE_FILES = LICENSE
XNNPACK_INSTALL_STAGING = YES
XNNPACK_DEPENDENCIES = cpuinfo fp16 fxdiv pthreadpool
XNNPACK_CONF_OPTS = \
	-DCMAKE_POSITION_INDEPENDENT_CODE=ON \
	-DXNNPACK_LIBRARY_TYPE:STRING=shared \
	-DXNNPACK_BUILD_TESTS=OFF \
	-DXNNPACK_BUILD_BENCHMARKS=OFF \
	-DXNNPACK_USE_SYSTEM_LIBS=ON

$(eval $(cmake-package))
