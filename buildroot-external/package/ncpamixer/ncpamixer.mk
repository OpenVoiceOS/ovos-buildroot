################################################################################
#
# ncpamixer
#
################################################################################

NCPAMIXER_VERSION = f2b18a48ce5dedcb24a3c8d39251eb7fbc2c1045
NCPAMIXER_SITE = $(call github,fulhax,ncpamixer,$(NCPAMIXER_VERSION))
NCPAMIXER_SUBDIR = src
NCPAMIXER_LICENSE = MIT

NCPAMIXER_INSTALL_STAGING = YES
NCPAMIXER_DEPENDENCIES = host-pkgconf
NCPAMIXER_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
