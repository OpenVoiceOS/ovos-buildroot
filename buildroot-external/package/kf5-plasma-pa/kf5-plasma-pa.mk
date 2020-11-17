################################################################################
#
# kf5-plasma-pa
#
################################################################################

KF5_PLASMA_PA_VERSION = 5.20.2
KF5_PLASMA_PA_SITE = https://download.kde.org/stable/plasma/$(KF5_PLASMA_PA_VERSION)
KF5_PLASMA_PA_SOURCE = plasma-pa-$(KF5_PLASMA_PA_VERSION).tar.xz
KF5_PLASMA_PA_LICENSE = BSD-3-Clause
KF5_PLASMA_PA_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_PLASMA_PA_DEPENDENCIES = host-pkgconf libcanberra kf5-plasma-framework kf5-kwayland
KF5_PLASMA_PA_INSTALL_STAGING = YES
KF5_PLASMA_PA_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
