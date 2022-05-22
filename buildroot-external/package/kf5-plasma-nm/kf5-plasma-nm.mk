################################################################################
#
# kf5-plasma-nm
#
################################################################################

KF5_PLASMA_NM_VERSION = 5.24.5
KF5_PLASMA_NM_SITE = https://download.kde.org/stable/plasma/$(KF5_PLASMA_NM_VERSION)
KF5_PLASMA_NM_SOURCE = plasma-nm-$(KF5_PLASMA_NM_VERSION).tar.xz
KF5_PLASMA_NM_LICENSE = BSD-3-Clause
KF5_PLASMA_NM_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_PLASMA_NM_DEPENDENCIES = host-pkgconf libcanberra kf5-plasma-framework \
				kf5-kwayland kf5-kwallet kf5-modemmanager-qt \
				kf5-prison kf5-qca

KF5_PLASMA_NM_INSTALL_STAGING = YES
KF5_PLASMA_NM_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
