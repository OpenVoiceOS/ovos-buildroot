################################################################################
#
# qtav
#
################################################################################

QTAV_VERSION = fdc613dc99304f208cff0bb25b3ded14bb993237
QTAV_SITE = $(call github,wang-bin,QtAV,$(QTAV_VERSION))

QTAV_INSTALL_STAGING = YES
QTAV_DEPENDENCIES = host-pkgconf
QTAV_SUPPORTS_IN_SOURCE_BUILD = NO
QTAV_SYNC_HEADERS = true

QTAV_CONF_OPTS = \
	-DBUILD_EXAMPLES=OFF \
	-DBUILD_TESTS=OFF

$(eval $(cmake-package))
