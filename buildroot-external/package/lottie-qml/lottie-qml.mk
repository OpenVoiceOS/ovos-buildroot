################################################################################
#
# lottie-qml
#
################################################################################

LOTTIE_QML_VERSION = 26335df22cfbb23cd238394792f05b94318c24c9
LOTTIE_QML_SITE = $(call github,kbroulik,lottie-qml,$(LOTTIE_QML_VERSION))
LOTTIE_QML_LICENSE = Apache License 2.0

LOTTIE_QML_INSTALL_STAGING = YES
LOTTIE_QML_DEPENDENCIES = host-pkgconf
LOTTIE_QML_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
