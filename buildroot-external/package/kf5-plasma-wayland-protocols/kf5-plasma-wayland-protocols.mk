################################################################################
#
# kf5-plasma-wayland-protocols.mk
#
################################################################################

KF5_PLASMA_WAYLAND_PROTOCOLS_VERSION = 1.7.0
KF5_PLASMA_WAYLAND_PROTOCOLS_SITE = https://download.kde.org/stable/plasma-wayland-protocols
KF5_PLASMA_WAYLAND_PROTOCOLS_SOURCE = plasma-wayland-protocols-$(KF5_PLASMA_WAYLAND_PROTOCOLS_VERSION).tar.xz
KF5_PLASMA_WAYLAND_PROTOCOLS_LICENSE = BSD-3-Clause
KF5_PLASMA_WAYLAND_PROTOCOLS_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_PLASMA_WAYLAND_PROTOCOLS_DEPENDENCIES = host-pkgconf
KF5_PLASMA_WAYLAND_PROTOCOLS_INSTALL_STAGING = YES
KF5_PLASMA_WAYLAND_PROTOCOLS_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
