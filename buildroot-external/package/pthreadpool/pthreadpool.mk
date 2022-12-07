################################################################################
#
# pthreadpool
#
################################################################################

PTHREADPOOL_VERSION = 545ebe9f225aec6dca49109516fac02e973a3de2
PTHREADPOOL_SITE = $(call github,Maratyszcza,pthreadpool,$(PTHREADPOOL_VERSION))
PTHREADPOOL_LICENSE = BSD-2-Clause
PTHREADPOOL_LICENSE_FILES = LICENSE

PTHREADPOOL_DEPENDENCIES = fxdiv
PTHREADPOOL_SUPPORTS_IN_SOURCE_BUILD = NO

PTHREADPOOL_CONF_OPTS = -DCMAKE_SYSTEM_NAME=Linux \
			-DCMAKE_SYSTEM_PROCESSOR=aarch64 \
			-DPTHREADPOOL_LIBRARY_TYPE=shared \
			-DPTHREADPOOL_BUILD_TESTS=OFF \
			-DPTHREADPOOL_BUILD_BENCHMARKS=OFF

PTHREADPOOL_INSTALL_STAGING = YES

$(eval $(cmake-package))
