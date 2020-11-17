################################################################################
#
# ncpamixer
#
################################################################################

NCPAMIXER_VERSION = 8cfb65955025b866cfc42215d1e4f51726944620
NCPAMIXER_SITE = $(call github,fulhax,ncpamixer,$(NCPAMIXER_VERSION))
NCPAMIXER_SUBDIR = src
NCPAMIXER_LICENSE = MIT

NCPAMIXER_INSTALL_STAGING = YES
NCPAMIXER_DEPENDENCIES = host-pkgconf
NCPAMIXER_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
