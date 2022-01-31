################################################################################
#
# kf5-pulseaudio-qt
#
################################################################################

KF5_PULSEAUDIO_QT_VERSION = 1.2
KF5_PULSEAUDIO_QT_SITE = https://download.kde.org/stable/pulseaudio-qt
KF5_PULSEAUDIO_QT_SOURCE = pulseaudio-qt-$(KF5_PULSEAUDIO_QT_VERSION).tar.xz
KF5_PULSEAUDIO_QT_LICENSE = BSD-3-Clause
KF5_PULSEAUDIO_QT_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_PULSEAUDIO_QT_DEPENDENCIES = host-pkgconf
KF5_PULSEAUDIO_QT_INSTALL_STAGING = YES
KF5_PULSEAUDIO_QT_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
