################################################################################
#
# mycroft-gui
#
################################################################################

MYCROFT_GUI_VERSION = f2f6636a4be02a6ac749999e21bd146f9cfda211
MYCROFT_GUI_SITE = $(call github,MycroftAI,mycroft-gui,$(MYCROFT_GUI_VERSION))
MYCROFT_GUI_LICENSE = Apache License 2.0

MYCROFT_GUI_INSTALL_STAGING = YES
MYCROFT_GUI_DEPENDENCIES = host-pkgconf
MYCROFT_GUI_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
