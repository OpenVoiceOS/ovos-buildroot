################################################################################
#
# kf5-knotifyconfig
#
################################################################################

KF5_KNOTIFYCONFIG_VERSION = $(KF5_VERSION)
KF5_KNOTIFYCONFIG_SITE = $(KF5_SITE)
KF5_KNOTIFYCONFIG_SOURCE = knotifyconfig-$(KF5_KNOTIFYCONFIG_VERSION).tar.xz
KF5_KNOTIFYCONFIG_LICENSE = BSD-3-Clause
KF5_KNOTIFYCONFIG_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KNOTIFYCONFIG_DEPENDENCIES = host-pkgconf qt5base kf5-phonon kf5-kcompletion \
				kf5-kconfig host-kf5-kconfig kf5-kio \
				host-kf5-kcoreaddons host-kf5-kauth
KF5_KNOTIFYCONFIG_INSTALL_STAGING = YES
KF5_KNOTIFYCONFIG_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
