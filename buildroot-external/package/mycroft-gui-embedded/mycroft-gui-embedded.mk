################################################################################
#
# mycroft-gui-embedded
#
################################################################################

MYCROFT_GUI_EMBEDDED_VERSION = cf6d9361c40252655a48711bb91fa895622af29d
MYCROFT_GUI_EMBEDDED_SITE = $(call github,j1nx,mycroft-gui-mark-2,$(MYCROFT_GUI_EMBEDDED_VERSION))
MYCROFT_GUI_EMBEDDED_LICENSE = Apache License 2.0

MYCROFT_GUI_EMBEDDED_INSTALL_STAGING = YES
MYCROFT_GUI_EMBEDDED_DEPENDENCIES = host-pkgconf
MYCROFT_GUI_EMBEDDED_SUPPORTS_IN_SOURCE_BUILD = NO

MYCROFT_GUI_EMBEDDED_CONF_OPTS += -DKF5_HOST_TOOLING="$(HOST_DIR)/lib/x86_64-linux-gnu/cmake"

$(eval $(cmake-package))
