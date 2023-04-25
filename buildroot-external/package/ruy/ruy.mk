################################################################################
#
# ruy
#
################################################################################

RUY_VERSION = 21a85fef159f9942f636a43b14c64b481c2a05b2
RUY_SITE = $(call github,google,ruy,$(RUY_VERSION))
RUY_LICENSE = Apache-2
RUY_LICENSE_FILES = LICENSE
RUY_INSTALL_STAGING = YES
RUY_DEPENDENCIES = cpuinfo
RUY_CONF_OPTS = -DCMAKE_POSITION_INDEPENDENT_CODE=ON \
		-DRUY_FIND_CPUINFO=ON \
		-DRUY_MINIMAL_BUILD=ON

$(eval $(cmake-package))
