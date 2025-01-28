################################################################################
#
# ncpamixer
#
################################################################################

NCPAMIXER_VERSION = 400d90e545fb3c139b83b41915bd2d458b92daf8
NCPAMIXER_SITE = $(call github,fulhax,ncpamixer,$(NCPAMIXER_VERSION))
NCPAMIXER_SUBDIR = src
NCPAMIXER_LICENSE = MIT

NCPAMIXER_INSTALL_STAGING = YES
NCPAMIXER_DEPENDENCIES = host-pkgconf
NCPAMIXER_SUPPORTS_IN_SOURCE_BUILD = NO
NCPAMIXER_CONF_OPTS = -DBUILD_MANPAGES=OFF

$(eval $(cmake-package))
