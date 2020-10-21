################################################################################
#
# kf5-kparts
#
################################################################################

KF5_KPARTS_VERSION = $(KF5_VERSION)
KF5_KPARTS_SITE = $(KF5_SITE)
KF5_KPARTS_SOURCE = kparts-$(KF5_KPARTS_VERSION).tar.xz
KF5_KPARTS_LICENSE = BSD-3-Clause
KF5_KPARTS_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KPARTS_DEPENDENCIES = host-pkgconf
KF5_KPARTS_INSTALL_STAGING = YES
KF5_KPARTS_SUPPORTS_IN_SOURCE_BUILD = NO

KF5_KPARTS_CONF_OPTS += -DKF5_HOST_TOOLING="$(HOST_DIR)/lib/x86_64-linux-gnu/cmake"

$(eval $(cmake-package))
