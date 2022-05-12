################################################################################
#
# kf5-kwin
#
################################################################################

KF5_KWIN_VERSION = 5.24.5
KF5_KWIN_SITE = https://download.kde.org/stable/plasma/$(KF5_KWIN_VERSION)
KF5_KWIN_SOURCE = kwin-$(KF5_KWIN_VERSION).tar.xz
KF5_KWIN_LICENSE = BSD-3-Clause
KF5_KWIN_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KWIN_DEPENDENCIES = host-pkgconf qt5sensors kf5-plasma-framework kf5-kwayland \
			kf5-kwayland-server kf5-kidletime kf5-kinit kf5-kcmutils \
			kf5-knewstuff kf5-attica kf5-kdecoration kf5-kscreenlocker
KF5_KWIN_INSTALL_STAGING = YES
KF5_KWIN_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
