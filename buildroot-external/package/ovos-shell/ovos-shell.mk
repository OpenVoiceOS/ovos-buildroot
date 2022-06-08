################################################################################
#
# ovos-shell
#
################################################################################

OVOS_SHELL_VERSION = f842f75bb8118ebd2bca012b578bcb717a8f9d93
OVOS_SHELL_SITE = $(call github,OpenVoiceOS,ovos-shell,$(OVOS_SHELL_VERSION))
OVOS_SHELL_LICENSE = Apache License 2.0

OVOS_SHELL_INSTALL_STAGING = YES
OVOS_SHELL_DEPENDENCIES = host-pkgconf
OVOS_SHELL_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
