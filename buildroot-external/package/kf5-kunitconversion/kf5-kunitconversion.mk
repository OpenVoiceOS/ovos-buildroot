################################################################################
#
# kf5-kunitconversion
#
################################################################################

KF5_KUNITCONVERSION_VERSION = $(KF5_VERSION)
KF5_KUNITCONVERSION_SITE = $(KF5_SITE)
KF5_KUNITCONVERSION_SOURCE = kunitconversion-$(KF5_KUNITCONVERSION_VERSION).tar.xz
KF5_KUNITCONVERSION_LICENSE = BSD-3-Clause
KF5_KUNITCONVERSION_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KUNITCONVERSION_DEPENDENCIES = host-pkgconf
KF5_KUNITCONVERSION_INSTALL_STAGING = YES
KF5_KUNITCONVERSION_SUPPORTS_IN_SOURCE_BUILD = NO

KF5_KUNITCONVERSION_CONF_OPTS += -DKF5_HOST_TOOLING="$(HOST_DIR)/lib/x86_64-linux-gnu/cmake"

$(eval $(cmake-package))
