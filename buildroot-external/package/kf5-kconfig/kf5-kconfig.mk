################################################################################
#
# kf5-kconfig
#
################################################################################

KF5_KCONFIG_VERSION = $(KF5_VERSION)
KF5_KCONFIG_SITE = $(KF5_SITE)
KF5_KCONFIG_SOURCE = kconfig-$(KF5_KCONFIG_VERSION).tar.xz

KF5_KCONFIG_DEPENDENCIES = \
	kf5-extra-cmake-modules \
	qt5tools \
	$(if $(BR2_PACKAGE_PYTHON3),python3)
KF5_KCONFIG_INSTALL_STAGING = YES
#KF5_KCONFIG_SUPPORTS_IN_SOURCE_BUILD = NO

KF5_KCONFIG_CXXFLAGS = $(TARGET_CXXFLAGS)

ifeq ($(BR2_TOOLCHAIN_HAS_LIBATOMIC),y)
	KF5_KCONFIG_CXXFLAGS += -latomic
endif

KF5_KCONFIG_CONF_OPTS = -DCMAKE_CXX_FLAGS="$(KF5_KCONFIG_CXXFLAGS)"

$(eval $(cmake-package))
