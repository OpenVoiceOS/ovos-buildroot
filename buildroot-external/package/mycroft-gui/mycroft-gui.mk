################################################################################
#
# mycroft-gui
#
################################################################################

MYCROFT_GUI_VERSION = 59cebdf574bd7500332ca529d792115520314cb6
MYCROFT_GUI_SITE = $(call github,MycroftAI,mycroft-gui,$(MYCROFT_GUI_VERSION))
MYCROFT_GUI_LICENSE = Apache License 2.0

MYCROFT_GUI_INSTALL_STAGING = YES
MYCROFT_GUI_DEPENDENCIES = host-pkgconf
MYCROFT_GUI_SUPPORTS_IN_SOURCE_BUILD = NO

define MYCROFT_GUI_CHANGE_IMAGE
	cp $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/mycroft-gui/background.png \
	$(@D)/application/
endef

MYCROFT_GUI_PRE_CONFIGURE_HOOKS += MYCROFT_GUI_CHANGE_IMAGE

$(eval $(cmake-package))
