################################################################################
#
# kf5-kdeconnect
#
################################################################################

KF5_KDECONNECT_VERSION = v22.04.1
KF5_KDECONNECT_SITE = $(call github,KDE,kdeconnect-kde,$(KF5_KDECONNECT_VERSION))

KF5_KDECONNECT_LICENSE = BSD-3-Clause
KF5_KDECONNECT_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KDECONNECT_DEPENDENCIES = host-pkgconf kf5-qca kf5-pulseaudio-qt kf5-kpeople \
				kf5-kirigami2 kf5-qqc2-desktop-style
KF5_KDECONNECT_INSTALL_STAGING = YES
KF5_KDECONNECT_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
