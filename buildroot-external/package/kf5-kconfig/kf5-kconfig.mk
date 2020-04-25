################################################################################
#
# kf5-kconfig
#
################################################################################

KF5_KCONFIG_VERSION = $(KF5_VERSION)
KF5_KCONFIG_SITE = $(KF5_SITE)
KF5_KCONFIG_SOURCE = kconfig-$(KF5_KCONFIG_VERSION).tar.xz
KF5_KCONFIG_LICENSE = BSD-3-Clause
KF5_KCONFIG_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KCONFIG_DEPENDENCIES = host-pkgconf
KF5_KCONFIG_INSTALL_STAGING = YES
KF5_KCONFIG_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
