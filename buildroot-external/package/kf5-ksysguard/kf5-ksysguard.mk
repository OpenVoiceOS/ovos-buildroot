################################################################################
#
# kf5-ksysguard
#
################################################################################

KF5_KSYSGUARD_VERSION = 5.20.2
KF5_KSYSGUARD_SITE = https://download.kde.org/stable/plasma/$(KF5_KSYSGUARD_VERSION)
KF5_KSYSGUARD_SOURCE = ksysguard-$(KF5_KSYSGUARD_VERSION).tar.xz
KF5_KSYSGUARD_LICENSE = BSD-3-Clause
KF5_KSYSGUARD_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KSYSGUARD_DEPENDENCIES = host-pkgconf kf5-libksysguard
KF5_KSYSGUARD_INSTALL_STAGING = YES
KF5_KSYSGUARD_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
