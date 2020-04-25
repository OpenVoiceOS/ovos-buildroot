################################################################################
#
# kf5-kguiaddons
#
################################################################################

KF5_KGUIADDONS_VERSION = $(KF5_VERSION)
KF5_KGUIADDONS_SITE = $(KF5_SITE)
KF5_KGUIADDONS_SOURCE = kguiaddons-$(KF5_KGUIADDONS_VERSION).tar.xz
KF5_KGUIADDONS_LICENSE = BSD-3-Clause
KF5_KGUIADDONS_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KGUIADDONS_DEPENDENCIES = host-pkgconf
KF5_KGUIADDONS_INSTALL_STAGING = YES
KF5_KGUIADDONS_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
