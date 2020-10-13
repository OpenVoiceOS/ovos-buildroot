################################################################################
#
# kf5-kdecoration
#
################################################################################

KF5_KDECORATION_VERSION = 5.18.5
KF5_KDECORATION_SITE = https://download.kde.org/stable/plasma/$(KF5_KDECORATION_VERSION)
KF5_KDECORATION_SOURCE = kdecoration-$(KF5_KDECORATION_VERSION).tar.xz
KF5_KDECORATION_LICENSE = BSD-3-Clause
KF5_KDECORATION_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KDECORATION_DEPENDENCIES = host-pkgconf libcanberra kf5-plasma-framework kf5-kwayland
KF5_KDECORATION_INSTALL_STAGING = YES
KF5_KDECORATION_SUPPORTS_IN_SOURCE_BUILD = NO

KF5_KDECORATION_CONF_OPTS += -DKF5_HOST_TOOLING="$(HOST_DIR)/lib/x86_64-linux-gnu/cmake"

$(eval $(cmake-package))
