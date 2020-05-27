################################################################################
#
# mycroft-gui
#
################################################################################

MYCROFT_GUI_VERSION = 5852d91ec587e78a937c79cc57e6d7f84f9a6aa2
MYCROFT_GUI_SITE = $(call github,MycroftAI,mycroft-gui,$(MYCROFT_GUI_VERSION))
MYCROFT_GUI_LICENSE = Apache License 2.0

MYCROFT_GUI_INSTALL_STAGING = YES
MYCROFT_GUI_DEPENDENCIES = host-pkgconf
MYCROFT_GUI_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
