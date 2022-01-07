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

KF5_KCONFIG_DEPENDENCIES = host-pkgconf #host-kf5-kconfig
KF5_KCONFIG_INSTALL_STAGING = YES
KF5_KCONFIG_SUPPORTS_IN_SOURCE_BUILD = NO

KF5_KCONFIG_CXXFLAGS = $(TARGET_CXXFLAGS)

ifeq ($(BR2_TOOLCHAIN_HAS_LIBATOMIC),y)
KF5_KCONFIG_CXXFLAGS += -latomic
endif

KF5_KCONFIG_CONF_OPTS = -DCMAKE_CXX_FLAGS="$(KF5_KCONFIG_CXXFLAGS)"

KF5_KCONFIG_POST_INSTALL_STAGING_HOOKS += KF5_KCONFIG_COPY_BINS

#define KF5_KCONFIG_COPY_BINS
#        cp ${HOST_DIR}/lib/x86_64-linux-gnu/libexec/kf5/kconfig_compiler_kf5 \
#	$(STAGING_DIR)/usr/lib/libexec/kf5/
#endef

$(eval $(cmake-package))

#HOST_KF5_KCONFIG_DEPENDENCIES = host-kf5-extra-cmake-modules
#HOST_KF5_KCONFIG_CXXFLAGS = $(HOST_CXXFLAGS)
#HOST_KF5_KCONFIG_CONF_OPTS = -DCMAKE_CXX_FLAGS="$(HOST_KF5_KCONFIG_CXXFLAGS)"

#$(eval $(host-cmake-package))
