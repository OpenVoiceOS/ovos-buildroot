################################################################################
#
# fxdiv
#
################################################################################

FXDIV_VERSION = b408327ac2a15ec3e43352421954f5b1967701d1
FXDIV_SITE = $(call github,Maratyszcza,FXdiv,$(FXDIV_VERSION))
FXDIV_LICENSE = BSD-2-Clause
FXDIV_LICENSE_FILES = LICENSE

FXDIV_SUPPORTS_IN_SOURCE_BUILD = NO

FXDIV_CONF_OPTS = -DCMAKE_SYSTEM_NAME=Linux \
                    -DCMAKE_SYSTEM_PROCESSOR=aarch64 \
		    -DFXDIV_BUILD_TESTS=OFF \
		    -DFXDIV_BUILD_BENCHMARKS=OFF

FXDIV_INSTALL_STAGING = YES
FXDIV_INSTALL_TARGET = NO

$(eval $(cmake-package))
