################################################################################
#
# kf5-phonon
#
################################################################################

KF5_PHONON_VERSION = 4.11.1
KF5_PHONON_SITE = https://download.kde.org/stable/phonon/$(KF5_PHONON_VERSION)
KF5_PHONON_SOURCE = phonon-$(KF5_PHONON_VERSION).tar.xz
KF5_PHONON_LICENSE = BSD-3-Clause
KF5_PHONON_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_PHONON_DEPENDENCIES = host-pkgconf
KF5_PHONON_INSTALL_STAGING = YES
KF5_PHONON_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
