################################################################################
#
# ncpamixer
#
################################################################################

NCPAMIXER_VERSION = a69610aa7dd2fb98a4b9558d0a0f73e14cc16aab
NCPAMIXER_SITE = $(call github,fulhax,ncpamixer,$(NCPAMIXER_VERSION))
NCPAMIXER_SUBDIR = src
NCPAMIXER_LICENSE = MIT

NCPAMIXER_INSTALL_STAGING = YES
NCPAMIXER_DEPENDENCIES = host-pkgconf
NCPAMIXER_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
