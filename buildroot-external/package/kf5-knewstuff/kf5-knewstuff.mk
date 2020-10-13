################################################################################
#
# kf5-knewstuff
#
################################################################################

KF5_KNEWSTUFF_VERSION = $(KF5_VERSION)
KF5_KNEWSTUFF_SITE = $(KF5_SITE)
KF5_KNEWSTUFF_SOURCE = knewstuff-$(KF5_KNEWSTUFF_VERSION).tar.xz
KF5_KNEWSTUFF_LICENSE = BSD-3-Clause
KF5_KNEWSTUFF_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KNEWSTUFF_DEPENDENCIES = host-pkgconf
KF5_KNEWSTUFF_INSTALL_STAGING = YES
KF5_KNEWSTUFF_SUPPORTS_IN_SOURCE_BUILD = NO

KF5_KNEWSTUFF_CONF_OPTS += -DKF5_HOST_TOOLING="$(HOST_DIR)/lib/x86_64-linux-gnu/cmake"

$(eval $(cmake-package))
