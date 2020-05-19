################################################################################
#
# mycroft-gui-embedded
#
################################################################################

MYCROFT_GUI_EMBEDDED_VERSION = cb734266ba1f3accaa158507008206620a3c2dde
MYCROFT_GUI_EMBEDDED_SITE = $(call github,MycroftAI,mycroft-gui-mark-2,$(MYCROFT_GUI_EMBEDDED_VERSION))
MYCROFT_GUI_EMBEDDED_LICENSE = Apache License 2.0

MYCROFT_GUI_EMBEDDED_INSTALL_STAGING = YES
MYCROFT_GUI_EMBEDDED_DEPENDENCIES = host-pkgconf
MYCROFT_GUI_EMBEDDED_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
