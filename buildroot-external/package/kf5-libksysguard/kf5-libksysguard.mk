################################################################################
#
# kf5-libksysguard
#
################################################################################

KF5_LIBKSYSGUARD_VERSION = 5.18.5
KF5_LIBKSYSGUARD_SITE = https://download.kde.org/stable/plasma/$(KF5_LIBKSYSGUARD_VERSION)
KF5_LIBKSYSGUARD_SOURCE = libksysguard-$(KF5_LIBKSYSGUARD_VERSION).tar.xz
KF5_LIBKSYSGUARD_LICENSE = BSD-3-Clause
KF5_LIBKSYSGUARD_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_LIBKSYSGUARD_DEPENDENCIES = host-pkgconf
KF5_LIBKSYSGUARD_INSTALL_STAGING = YES
KF5_LIBKSYSGUARD_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
