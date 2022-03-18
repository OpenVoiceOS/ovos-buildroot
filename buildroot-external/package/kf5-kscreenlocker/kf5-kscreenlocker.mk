################################################################################
#
# kf5-kscreenlocker
#
################################################################################

KF5_KSCREENLOCKER_VERSION = 5.20.2
KF5_KSCREENLOCKER_SITE = https://download.kde.org/stable/plasma/$(KF5_KSCREENLOCKER_VERSION)
KF5_KSCREENLOCKER_SOURCE = kscreenlocker-$(KF5_KSCREENLOCKER_VERSION).tar.xz
KF5_KSCREENLOCKER_LICENSE = BSD-3-Clause
KF5_KSCREENLOCKER_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KSCREENLOCKER_DEPENDENCIES = host-pkgconf kf5-plasma-framework kf5-kwayland
KF5_KSCREENLOCKER_INSTALL_STAGING = YES
KF5_KSCREENLOCKER_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
