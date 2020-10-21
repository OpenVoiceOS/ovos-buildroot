################################################################################
#
# kf5-plasma-nano
#
################################################################################

KF5_PLASMA_NANO_VERSION = 5.18.5
KF5_PLASMA_NANO_SITE = https://download.kde.org/stable/plasma/$(KF5_PLASMA_NANO_VERSION)
KF5_PLASMA_NANO_SOURCE = plasma-nano-$(KF5_PLASMA_NANO_VERSION).tar.xz
KF5_PLASMA_NANO_LICENSE = BSD-3-Clause
KF5_PLASMA_NANO_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_PLASMA_NANO_DEPENDENCIES = host-pkgconf kf5-plasma-framework kf5-kwayland
KF5_PLASMA_NANO_INSTALL_STAGING = YES
KF5_PLASMA_NANO_SUPPORTS_IN_SOURCE_BUILD = NO

KF5_PLASMA_NANO_CONF_OPTS += -DKF5_HOST_TOOLING="$(HOST_DIR)/lib/x86_64-linux-gnu/cmake"

$(eval $(cmake-package))
