################################################################################
#
# kf5-qqc2-desktop-style
#
################################################################################

KF5_QQC2_DESKTOP_STYLE_VERSION = $(KF5_VERSION)
KF5_QQC2_DESKTOP_STYLE_SITE = $(KF5_SITE)
KF5_QQC2_DESKTOP_STYLE_SOURCE = qqc2-desktop-style-$(KF5_QQC2_DESKTOP_STYLE_VERSION).tar.xz
KF5_QQC2_DESKTOP_STYLE_LICENSE = BSD-3-Clause
KF5_QQC2_DESKTOP_STYLE_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_QQC2_DESKTOP_STYLE_DEPENDENCIES = host-pkgconf
KF5_QQC2_DESKTOP_STYLE_INSTALL_STAGING = YES
KF5_QQC2_DESKTOP_STYLE_SUPPORTS_IN_SOURCE_BUILD = NO

KF5_QQC2_DESKTOP_STYLE_CONF_OPTS += -DKF5_HOST_TOOLING="$(HOST_DIR)/lib/x86_64-linux-gnu/cmake"

$(eval $(cmake-package))
