################################################################################
#
# kf5-plasma-workspace
#
################################################################################

KF5_PLASMA_WORKSPACE_VERSION = 5.18.5
KF5_PLASMA_WORKSPACE_SITE = https://download.kde.org/stable/plasma/$(KF5_PLASMA_WORKSPACE_VERSION)
KF5_PLASMA_WORKSPACE_SOURCE = plasma-workspace-$(KF5_PLASMA_WORKSPACE_VERSION).tar.xz
KF5_PLASMA_WORKSPACE_LICENSE = BSD-3-Clause
KF5_PLASMA_WORKSPACE_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_PLASMA_WORKSPACE_DEPENDENCIES = host-pkgconf kf5-plasma-framework kf5-kwayland
KF5_PLASMA_WORKSPACE_INSTALL_STAGING = YES
KF5_PLASMA_WORKSPACE_SUPPORTS_IN_SOURCE_BUILD = NO

KF5_PLASMA_WORKSPACE_CONF_OPTS += -DKF5_HOST_TOOLING="$(HOST_DIR)/lib/x86_64-linux-gnu/cmake"

$(eval $(cmake-package))
