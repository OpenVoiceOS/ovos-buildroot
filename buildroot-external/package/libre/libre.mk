#############################################################
#
# libre
#
#############################################################

LIBRE_VERSION = 2.7.0
LIBRE_SOURCE = v$(LIBRE_VERSION).tar.gz
LIBRE_SITE = https://github.com/baresip/re/archive
LIBRE_INSTALL_STAGING = YES

ifeq ($(BR2_PACKAGE_OPENSSL),y)
LIBRE_DEPENDENCIES += openssl
endif
ifeq ($(BR2_PACKAGE_ZLIB),y)
LIBRE_DEPENDENCIES += zlib
endif

$(eval $(cmake-package))
