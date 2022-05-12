################################################################################
#
# kf5-layer-shell-qt
#
################################################################################

KF5_LAYER_SHELL_QT_VERSION = 5.24.5
KF5_LAYER_SHELL_QT_SITE = https://download.kde.org/stable/plasma/$(KF5_LAYER_SHELL_QT_VERSION)
KF5_LAYER_SHELL_QT_SOURCE = layer-shell-qt-$(KF5_LAYER_SHELL_QT_VERSION).tar.xz
KF5_LAYER_SHELL_QT_LICENSE = BSD-3-Clause
KF5_LAYER_SHELL_QT_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_LAYER_SHELL_QT_DEPENDENCIES = host-pkgconf kf5-plasma-framework kf5-kwayland
KF5_LAYER_SHELL_QT_INSTALL_STAGING = YES
KF5_LAYER_SHELL_QT_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
