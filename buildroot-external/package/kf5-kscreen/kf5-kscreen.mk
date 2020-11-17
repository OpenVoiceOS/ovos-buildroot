################################################################################
#
# kf5-kscreen
#
################################################################################

KF5_KSCREEN_VERSION = 5.20.2
KF5_KSCREEN_SITE = https://download.kde.org/stable/plasma/$(KF5_KSCREEN_VERSION)
KF5_KSCREEN_SOURCE = kscreen-$(KF5_KSCREEN_VERSION).tar.xz
KF5_KSCREEN_LICENSE = BSD-3-Clause
KF5_KSCREEN_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KSCREEN_DEPENDENCIES = host-pkgconf kf5-libkscreen
KF5_KSCREEN_INSTALL_STAGING = YES
KF5_KSCREEN_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
