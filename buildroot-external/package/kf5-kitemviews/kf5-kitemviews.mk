################################################################################
#
# kf5-kitemviews
#
################################################################################

KF5_KITEMVIEWS_VERSION = $(KF5_VERSION)
KF5_KITEMVIEWS_SITE = $(KF5_SITE)
KF5_KITEMVIEWS_SOURCE = kitemviews-$(KF5_KITEMVIEWS_VERSION).tar.xz
KF5_KITEMVIEWS_LICENSE = BSD-3-Clause
KF5_KITEMVIEWS_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KITEMVIEWS_DEPENDENCIES = host-pkgconf kf5-kiconthemes
KF5_KITEMVIEWS_INSTALL_STAGING = YES
KF5_KITEMVIEWS_SUPPORTS_IN_SOURCE_BUILD = NO

KF5_KITEMVIEWS_CONF_OPTS = -DBUILD_DESIGNERPLUGIN=OFF

$(eval $(cmake-package))
