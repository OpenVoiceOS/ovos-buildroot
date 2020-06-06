################################################################################
#
# kf5-breeze-icons
#
################################################################################

KF5_BREEZE_ICONS_VERSION = $(KF5_VERSION)
KF5_BREEZE_ICONS_SITE = $(KF5_SITE)
KF5_BREEZE_ICONS_SOURCE = breeze-icons-$(KF5_BREEZE_ICONS_VERSION).tar.xz
KF5_BREEZE_ICONS_LICENSE = BSD-3-Clause
KF5_BREEZE_ICONS_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_BREEZE_ICONS_DEPENDENCIES = host-pkgconf
KF5_BREEZE_ICONS_INSTALL_STAGING = YES
KF5_BREEZE_ICONS_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
