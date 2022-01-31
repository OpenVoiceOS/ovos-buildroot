################################################################################
#
# kf5-qca
#
################################################################################

KF5_QCA_VERSION = 2.3.4
KF5_QCA_SITE = https://download.kde.org/stable/qca/$(KF5_QCA_VERSION)
KF5_QCA_SOURCE = qca-$(KF5_QCA_VERSION).tar.xz
KF5_QCA_LICENSE = BSD-3-Clause
KF5_QCA_LICENSE_FILES = COPYING-CMAKE-SCRIPTS

KF5_QCA_DEPENDENCIES = host-pkgconf
KF5_QCA_INSTALL_STAGING = YES
KF5_QCA_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
