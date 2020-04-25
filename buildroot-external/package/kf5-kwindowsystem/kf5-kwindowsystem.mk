################################################################################
#
# kf5-kwindowsystem
#
################################################################################

KF5_KWINDOWSYSTEM_VERSION = $(KF5_VERSION)
KF5_KWINDOWSYSTEM_SITE = $(KF5_SITE)
KF5_KWINDOWSYSTEM_SOURCE = kwindowsystem-$(KF5_KWINDOWSYSTEM_VERSION).tar.xz
KF5_KWINDOWSYSTEM_LICENSE = BSD-3-Clause
KF5_KWINDOWSYSTEM_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KWINDOWSYSTEM_DEPENDENCIES = host-pkgconf
KF5_KWINDOWSYSTEM_INSTALL_STAGING = YES
KF5_KWINDOWSYSTEM_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
