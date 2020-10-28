################################################################################
#
# kf5-plasma-framework
#
################################################################################

KF5_PLASMA_FRAMEWORK_VERSION = $(KF5_VERSION)
KF5_PLASMA_FRAMEWORK_SITE = $(KF5_SITE)
KF5_PLASMA_FRAMEWORK_SOURCE = plasma-framework-$(KF5_PLASMA_FRAMEWORK_VERSION).tar.xz
KF5_PLASMA_FRAMEWORK_LICENSE = BSD-3-Clause
KF5_PLASMA_FRAMEWORK_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_PLASMA_FRAMEWORK_DEPENDENCIES = host-pkgconf kf5-kdoctools kf5-kirigami2
KF5_PLASMA_FRAMEWORK_INSTALL_STAGING = YES

KF5_PLASMA_FRAMEWORK_CONF_OPTS += -DHAVE_EGL=1
KF5_PLASMA_FRAMEWORK_CONF_OPTS += -DEGL_INCLUDE_DIR="$(STAGING_DIR)/usr/include"
KF5_PLASMA_FRAMEWORK_CONF_OPTS += -DEGL_LIBRARY="$(STAGING_DIR)/usr/lib/libEGL.so"

$(eval $(cmake-package))
