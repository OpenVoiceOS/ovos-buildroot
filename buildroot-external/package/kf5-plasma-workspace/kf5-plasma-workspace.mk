################################################################################
#
# kf5-plasma-workspace
#
################################################################################

KF5_PLASMA_WORKSPACE_VERSION = 5.20.2
KF5_PLASMA_WORKSPACE_SITE = https://download.kde.org/stable/plasma/$(KF5_PLASMA_WORKSPACE_VERSION)
KF5_PLASMA_WORKSPACE_SOURCE = plasma-workspace-$(KF5_PLASMA_WORKSPACE_VERSION).tar.xz
KF5_PLASMA_WORKSPACE_LICENSE = BSD-3-Clause
KF5_PLASMA_WORKSPACE_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_PLASMA_WORKSPACE_DEPENDENCIES = host-pkgconf libcanberra kf5-plasma-framework kf5-kwayland \
					kf5-kdelibs4support kf5-krunner kf5-knotifyconfig \
					kf5-kdesu kf5-kwallet kf5-kitemmodels kf5-kpeople \
					kf5-kactivities-stats kf5-ksysguard kf5-kscreen \
					kf5-prison

KF5_PLASMA_WORKSPACE_INSTALL_STAGING = YES
KF5_PLASMA_WORKSPACE_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
