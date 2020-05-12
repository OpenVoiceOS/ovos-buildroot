################################################################################
#
# kf5-kpackage
#
################################################################################

KF5_KPACKAGE_VERSION = $(KF5_VERSION)
KF5_KPACKAGE_SITE = $(KF5_SITE)
KF5_KPACKAGE_SOURCE = kpackage-$(KF5_KPACKAGE_VERSION).tar.xz
KF5_KPACKAGE_LICENSE = BSD-3-Clause
KF5_KPACKAGE_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KPACKAGE_DEPENDENCIES = host-pkgconf
KF5_KPACKAGE_INSTALL_STAGING = YES
KF5_KPACKAGE_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))

HOST_KF5_KPACKAGE_DEPENDENCIES = host-kf5-extra-cmake-modules host-kf5-karchive \
				 host-kf5-ki18n

HOST_KF5_KPACKAGE_CXXFLAGS = $(HOST_CXXFLAGS)
HOST_KF5_KPACKAGE_CONF_OPTS = -DCMAKE_CXX_FLAGS="$(HOST_KF5_KPACKAGE_CXXFLAGS)"

$(eval $(host-cmake-package))
