################################################################################
#
# userland-tools
#
################################################################################

USERLAND_TOOLS_VERSION = 14b90ff9d9f031391a299e6e006965d02bfd1bb1
USERLAND_TOOLS_SITE = $(call github,raspberrypi,userland,$(USERLAND_TOOLS_VERSION))
USERLAND_TOOLS_LICENSE = BSD-3-Clause
USERLAND_TOOLS_LICENSE_FILES = LICENCE
USERLAND_TOOLS_CONF_OPTS = -DVMCS_INSTALL_PREFIX=/usr -DALL_APPS=OFF -DARM64=y

$(eval $(cmake-package))
