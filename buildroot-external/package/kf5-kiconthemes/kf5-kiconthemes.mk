################################################################################
#
# kf5-kiconthemes
#
################################################################################

KF5_KICONTHEMES_VERSION = $(KF5_VERSION)
KF5_KICONTHEMES_SITE = $(KF5_SITE)
KF5_KICONTHEMES_SOURCE = kiconthemes-$(KF5_KICONTHEMES_VERSION).tar.xz
KF5_KICONTHEMES_LICENSE = BSD-3-Clause
KF5_KICONTHEMES_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KICONTHEMES_DEPENDENCIES = host-pkgconf
KF5_KICONTHEMES_INSTALL_STAGING = YES
KF5_KICONTHEMES_SUPPORTS_IN_SOURCE_BUILD = NO

KF5_KICONTHEMES_CONF_OPTS = -DBUILD_DESIGNERPLUGIN=OFF

$(eval $(cmake-package))
