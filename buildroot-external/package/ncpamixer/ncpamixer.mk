################################################################################
#
# ncpamixer
#
################################################################################

NCPAMIXER_VERSION = a273d233437caa31348fe3ffd8cfdd7c3d3d27c7
NCPAMIXER_SITE = $(call github,fulhax,ncpamixer,$(NCPAMIXER_VERSION))
NCPAMIXER_SUBDIR = src
NCPAMIXER_LICENSE = MIT

NCPAMIXER_INSTALL_STAGING = YES
NCPAMIXER_DEPENDENCIES = host-pkgconf
NCPAMIXER_SUPPORTS_IN_SOURCE_BUILD = NO
NCPAMIXER_CONF_OPTS = -DBUILD_MANPAGES=OFF

$(eval $(cmake-package))
