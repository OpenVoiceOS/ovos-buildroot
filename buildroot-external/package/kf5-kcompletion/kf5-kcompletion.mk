################################################################################
#
# kf5-kcompletion
#
################################################################################

KF5_KCOMPLETION_VERSION = $(KF5_VERSION)
KF5_KCOMPLETION_SITE = $(KF5_SITE)
KF5_KCOMPLETION_SOURCE = kcompletion-$(KF5_KCOMPLETION_VERSION).tar.xz
KF5_KCOMPLETION_LICENSE = BSD-3-Clause
KF5_KCOMPLETION_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KCOMPLETION_DEPENDENCIES = host-pkgconf
KF5_KCOMPLETION_INSTALL_STAGING = YES
KF5_KCOMPLETION_SUPPORTS_IN_SOURCE_BUILD = NO

KF5_KCOMPLETION_CONF_OPTS = -DBUILD_DESIGNERPLUGIN=OFF

$(eval $(cmake-package))
