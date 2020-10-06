################################################################################
#
# mycroft-embedded-shell
#
################################################################################

MYCROFT_EMBEDDED_SHELL_VERSION = 7432502b42c0d2f1c2e15abfc666f000455f7e99
MYCROFT_EMBEDDED_SHELL_SITE = $(call github,notmart,mycroft-embedded-shell,$(MYCROFT_EMBEDDED_SHELL_VERSION))
MYCROFT_EMBEDDED_SHELL_LICENSE = Apache License 2.0

MYCROFT_EMBEDDED_SHELL_INSTALL_STAGING = YES
MYCROFT_EMBEDDED_SHELL_DEPENDENCIES = host-pkgconf
MYCROFT_EMBEDDED_SHELL_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
