################################################################################
#
# ovos-shell
#
################################################################################

OVOS_SHELL_VERSION = 13ec34163bf9048d4544f2e48f6a9b7f00b2d89e
OVOS_SHELL_SITE = $(call github,OpenVoiceOS,ovos-shell,$(OVOS_SHELL_VERSION))
OVOS_SHELL_LICENSE = Apache License 2.0

OVOS_SHELL_INSTALL_STAGING = YES
OVOS_SHELL_DEPENDENCIES = host-pkgconf
OVOS_SHELL_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
