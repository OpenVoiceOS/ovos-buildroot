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

KF5_PLASMA_FRAMEWORK_DEPENDENCIES = host-pkgconf
KF5_PLASMA_FRAMEWORK_INSTALL_STAGING = YES
KF5_PLASMA_FRAMEWORK_INSTALL_TARGET = NO

$(eval $(cmake-package))
