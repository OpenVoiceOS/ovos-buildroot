################################################################################
#
# kf5-kdeclarative
#
################################################################################

KF5_KDECLARATIVE_VERSION = $(KF5_VERSION)
KF5_KDECLARATIVE_SITE = $(KF5_SITE)
KF5_KDECLARATIVE_SOURCE = kdeclarative-$(KF5_KDECLARATIVE_VERSION).tar.xz
KF5_KDECLARATIVE_LICENSE = BSD-3-Clause
KF5_KDECLARATIVE_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KDECLARATIVE_DEPENDENCIES = host-pkgconf kf5-kio kf5-kpackage #host-kf5-kpackage
KF5_KDECLARATIVE_INSTALL_STAGING = YES
KF5_KDECLARATIVE_SUPPORTS_IN_SOURCE_BUILD = NO

#KF5_KDECLARATIVE_CONF_OPTS += -DKF5_HOST_TOOLING=$(HOST_DIR)/lib/x86_64-linux-gnu/cmake

$(eval $(cmake-package))
