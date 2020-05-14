################################################################################
#
# kf5-ki18n
#
################################################################################

KF5_KI18N_VERSION = $(KF5_VERSION)
KF5_KI18N_SITE = $(KF5_SITE)
KF5_KI18N_SOURCE = ki18n-$(KF5_KI18N_VERSION).tar.xz
KF5_KI18N_LICENSE = BSD-3-Clause
KF5_KI18N_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KI18N_DEPENDENCIES = host-pkgconf
KF5_KI18N_INSTALL_STAGING = YES
KF5_KI18N_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))

HOST_KF5_KI18N_DEPENDENCIES = host-kf5-extra-cmake-modules
HOST_KF5_KI18N_CXXFLAGS = $(HOST_CXXFLAGS)
HOST_KF5_KI18N_CONF_OPTS = -DCMAKE_CXX_FLAGS="$(HOST_KF5_KI18N_CXXFLAGS)"

$(eval $(host-cmake-package))
