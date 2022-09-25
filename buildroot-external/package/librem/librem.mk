#############################################################
#
# librem
#
#############################################################

LIBREM_VERSION = 2.7.0
LIBREM_SOURCE = v$(LIBREM_VERSION).tar.gz
LIBREM_SITE = https://github.com/baresip/rem/archive
LIBREM_INSTALL_STAGING = YES

ifeq ($(BR2_PACKAGE_LIBRE),y)
LIBREM_DEPENDENCIES += libre
endif

$(eval $(cmake-package))
