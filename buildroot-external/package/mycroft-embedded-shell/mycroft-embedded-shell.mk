################################################################################
#
# mycroft-embedded-shell
#
################################################################################

MYCROFT_EMBEDDED_SHELL_VERSION = 0e3fa2e79f3beb0c37f1d2cf1db2f8fb22189415
MYCROFT_EMBEDDED_SHELL_SITE = $(call github,OpenVoiceOS,mycroft-embedded-shell,$(MYCROFT_EMBEDDED_SHELL_VERSION))
MYCROFT_EMBEDDED_SHELL_LICENSE = Apache License 2.0

MYCROFT_EMBEDDED_SHELL_INSTALL_STAGING = YES
MYCROFT_EMBEDDED_SHELL_DEPENDENCIES = host-pkgconf
MYCROFT_EMBEDDED_SHELL_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
