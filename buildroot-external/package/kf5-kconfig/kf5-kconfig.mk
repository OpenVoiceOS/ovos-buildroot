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

KF5_KCONFIG_CXXFLAGS = $(TARGET_CXXFLAGS)

ifeq ($(BR2_TOOLCHAIN_HAS_LIBATOMIC),y)
KF5_KCONFIG_CXXFLAGS += -latomic
endif

KF5_KCONFIG_CONF_OPTS = -DCMAKE_CXX_FLAGS="$(KF5_KCONFIG_CXXFLAGS)"

$(eval $(cmake-package))
