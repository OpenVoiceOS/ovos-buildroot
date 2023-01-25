################################################################################
#
# opencl_headers
#
################################################################################

OPENCL_HEADERS_VERSION = dcd5bede6859d26833cd85f0d6bbcee7382dc9b3
OPENCL_HEADERS_SITE = $(call github,KhronosGroup,OpenCL-Headers,$(OPENCL_HEADERS_VERSION))
OPENCL_HEADERS_LICENSE = BSD-2-Clause
OPENCL_HEADERS_LICENSE_FILES = LICENSE

OPENCL_HEADERS_SUPPORTS_IN_SOURCE_BUILD = NO
OPENCL_HEADERS_DEPENDENCIES = psimd

OPENCL_HEADERS_CONF_OPTS = -DCMAKE_SYSTEM_NAME=Linux \
		 -DCMAKE_SYSTEM_PROCESSOR=aarch64 \
		 -DOPENCL_HEADERS_BUILD_TESTING=OFF \
		 -DOPENCL_HEADERS_BUILD_CXX_TESTS=OFF

OPENCL_HEADERS_INSTALL_STAGING = YES
OPENCL_HEADERS_INSTALL_TARGET = NO

$(eval $(cmake-package))
