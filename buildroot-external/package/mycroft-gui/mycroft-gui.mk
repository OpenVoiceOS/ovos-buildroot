################################################################################
#
# mycroft-gui
#
################################################################################

MYCROFT_GUI_VERSION = 3bfd5d862ecfbd9d7a7c8391a9d2cee1fa3cbf00
MYCROFT_GUI_SITE = $(call github,MycroftAI,mycroft-gui,$(MYCROFT_GUI_VERSION))
MYCROFT_GUI_LICENSE = Apache License 2.0

MYCROFT_GUI_INSTALL_STAGING = YES
MYCROFT_GUI_DEPENDENCIES = host-pkgconf kf5-kirigami2 lottie-qml
MYCROFT_GUI_SUPPORTS_IN_SOURCE_BUILD = NO

define MYCROFT_GUI_CHANGE_IMAGE
	cp $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/mycroft-gui/background.png \
	$(@D)/application/
endef

define MYCROFT_GUI_CHANGE_STATUS
        cp $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/mycroft-gui/StatusIndicator.qml \
        $(@D)/import/qml/
endef

MYCROFT_GUI_PRE_CONFIGURE_HOOKS += MYCROFT_GUI_CHANGE_IMAGE
MYCROFT_GUI_PRE_CONFIGURE_HOOKS += MYCROFT_GUI_CHANGE_STATUS

$(eval $(cmake-package))
