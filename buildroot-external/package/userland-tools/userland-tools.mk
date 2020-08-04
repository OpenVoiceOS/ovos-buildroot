################################################################################
#
# userland-tools
#
################################################################################

USERLAND_TOOLS_VERSION = 3e59217bd93b8024fb8fc1c6530b00cbae64bc73
USERLAND_TOOLS_SITE = $(call github,raspberrypi,userland,$(USERLAND_TOOLS_VERSION))
USERLAND_TOOLS_LICENSE = BSD-3-Clause
USERLAND_TOOLS_LICENSE_FILES = LICENCE
USERLAND_TOOLS_CONF_OPTS = -DVMCS_INSTALL_PREFIX=/usr -DALL_APPS=OFF -DARM64=y

$(eval $(cmake-package))
