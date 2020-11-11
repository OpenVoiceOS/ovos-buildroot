################################################################################
#
# kf5-kwayland-server
#
################################################################################

KF5_KWAYLAND_SERVER_VERSION = 5.20.2
KF5_KWAYLAND_SERVER_SITE = https://download.kde.org/stable/plasma/$(KF5_KWAYLAND_SERVER_VERSION)
KF5_KWAYLAND_SERVER_SOURCE = kwayland-server-$(KF5_KWAYLAND_SERVER_VERSION).tar.xz
KF5_KWAYLAND_SERVER_LICENSE = BSD-3-Clause
KF5_KWAYLAND_SERVER_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KWAYLAND_SERVER_DEPENDENCIES = host-pkgconf kf5-kwayland
KF5_KWAYLAND_SERVER_INSTALL_STAGING = YES
KF5_KWAYLAND_SERVER_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
