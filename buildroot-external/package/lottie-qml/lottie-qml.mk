################################################################################
#
# lottie-qml
#
################################################################################

LOTTIE_QML_VERSION = 0db824cfea0cbefff775c3caa4918719f45762ca
LOTTIE_QML_SITE = $(call github,kbroulik,lottie-qml,$(LOTTIE_QML_VERSION))
LOTTIE_QML_LICENSE = Apache License 2.0

LOTTIE_QML_INSTALL_STAGING = YES
LOTTIE_QML_DEPENDENCIES = host-pkgconf
LOTTIE_QML_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
