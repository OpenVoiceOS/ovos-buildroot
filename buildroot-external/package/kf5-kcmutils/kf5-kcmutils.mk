################################################################################
#
# kf5-kcmutils
#
################################################################################

KF5_KCMUTILS_VERSION = $(KF5_VERSION)
KF5_KCMUTILS_SITE = $(KF5_SITE)
KF5_KCMUTILS_SOURCE = kcmutils-$(KF5_KCMUTILS_VERSION).tar.xz
KF5_KCMUTILS_LICENSE = BSD-3-Clause
KF5_KCMUTILS_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KCMUTILS_DEPENDENCIES = host-pkgconf
KF5_KCMUTILS_INSTALL_STAGING = YES
KF5_KCMUTILS_SUPPORTS_IN_SOURCE_BUILD = NO

KF5_KCMUTILS_CONF_OPTS += -DKF5_HOST_TOOLING="$(HOST_DIR)/lib/x86_64-linux-gnu/cmake"

$(eval $(cmake-package))
