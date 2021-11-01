################################################################################
#
# mycroft-embedded-shell
#
################################################################################

MYCROFT_EMBEDDED_SHELL_VERSION = accde096d0e213b3701efe9e0ad7a904b6791633
MYCROFT_EMBEDDED_SHELL_SITE = $(call github,OpenVoiceOS,mycroft-embedded-shell,$(MYCROFT_EMBEDDED_SHELL_VERSION))
MYCROFT_EMBEDDED_SHELL_LICENSE = Apache License 2.0

MYCROFT_EMBEDDED_SHELL_INSTALL_STAGING = YES
MYCROFT_EMBEDDED_SHELL_DEPENDENCIES = host-pkgconf
MYCROFT_EMBEDDED_SHELL_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
