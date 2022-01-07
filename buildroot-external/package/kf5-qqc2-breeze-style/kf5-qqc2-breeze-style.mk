################################################################################
#
# kf5-qqc2-breeze-style
#
################################################################################

KF5_QQC2_BREEZE_STYLE_VERSION = 5.21.5
KF5_QQC2_BREEZE_STYLE_SITE = https://download.kde.org/stable/plasma/$(KF5_QQC2_BREEZE_STYLE_VERSION)
KF5_QQC2_BREEZE_STYLE_SOURCE = qqc2-breeze-style-$(KF5_QQC2_BREEZE_STYLE_VERSION).tar.xz
KF5_QQC2_BREEZE_STYLE_LICENSE = BSD-3-Clause
KF5_QQC2_BREEZE_STYLE_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_QQC2_BREEZE_STYLE_DEPENDENCIES = host-pkgconf
KF5_QQC2_BREEZE_STYLE_INSTALL_STAGING = YES
KF5_QQC2_BREEZE_STYLE_SUPPORTS_IN_SOURCE_BUILD = NO

#KF5_QQC2_BREEZE_STYLE_CONF_OPTS += -DKF5_HOST_TOOLING="$(HOST_DIR)/lib/x86_64-linux-gnu/cmake"

$(eval $(cmake-package))
