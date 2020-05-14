################################################################################
#
# kf5-kglobalaccel
#
################################################################################

KF5_KGLOBALACCEL_VERSION = $(KF5_VERSION)
KF5_KGLOBALACCEL_SITE = $(KF5_SITE)
KF5_KGLOBALACCEL_SOURCE = kglobalaccel-$(KF5_KGLOBALACCEL_VERSION).tar.xz
KF5_KGLOBALACCEL_LICENSE = BSD-3-Clause
KF5_KGLOBALACCEL_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_KGLOBALACCEL_DEPENDENCIES = host-pkgconf kf5-kcrash kf5-kdbusaddons
KF5_KGLOBALACCEL_INSTALL_STAGING = YES
KF5_KGLOBALACCEL_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
