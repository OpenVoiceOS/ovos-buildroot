################################################################################
#
# kf5-kauth
#
################################################################################

KF5_KAUTH_VERSION = $(KF5_VERSION)
KF5_KAUTH_SITE = $(KF5_SITE)
KF5_KAUTH_SOURCE = kauth-$(KF5_KAUTH_VERSION).tar.xz
KF5_KAUTH_LICENSE = BSD-3-Clause
KF5_KAUTH_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KAUTH_DEPENDENCIES = host-pkgconf
KF5_KAUTH_INSTALL_STAGING = YES
KF5_KAUTH_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))

HOST_KF5_KAUTH_DEPENDENCIES = host-kf5-extra-cmake-modules
HOST_KF5_KAUTH_CXXFLAGS = $(HOST_CXXFLAGS)
HOST_KF5_KAUTH_CONF_OPTS = -DCMAKE_CXX_FLAGS="$(HOST_KF5_KAUTH_CXXFLAGS)"

$(eval $(host-cmake-package))
