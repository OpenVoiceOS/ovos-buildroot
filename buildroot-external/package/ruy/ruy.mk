################################################################################
#
# ruy
#
################################################################################

RUY_VERSION = 3168a5c8f4c447fd8cea94078121ee2e2cd87df0
RUY_SITE = $(call github,google,ruy,$(RUY_VERSION))
RUY_LICENSE = Apache-2
RUY_LICENSE_FILES = LICENSE
RUY_DEPENDENCIES = cpuinfo
RUY_SUPPORTS_IN_SOURCE_BUILD = NO
RUY_CONF_OPTS = -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
		-DRUY_FIND_CPUINFO=ON \
		-DRUY_MINIMAL_BUILD=ON

RUY_INSTALL_STAGING = YES

$(eval $(cmake-package))
