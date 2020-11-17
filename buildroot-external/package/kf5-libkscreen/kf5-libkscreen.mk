################################################################################
#
# kf5-libkscreen
#
################################################################################

KF5_LIBKSCREEN_VERSION = 5.20.2
KF5_LIBKSCREEN_SITE = https://download.kde.org/stable/plasma/$(KF5_LIBKSCREEN_VERSION)
KF5_LIBKSCREEN_SOURCE = libkscreen-$(KF5_LIBKSCREEN_VERSION).tar.xz
KF5_LIBKSCREEN_LICENSE = BSD-3-Clause
KF5_LIBKSCREEN_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_LIBKSCREEN_DEPENDENCIES = host-pkgconf
KF5_LIBKSCREEN_INSTALL_STAGING = YES
KF5_LIBKSCREEN_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
