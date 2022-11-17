################################################################################
#
# ovos-shell
#
################################################################################

OVOS_SHELL_VERSION = 293706bf1bbcb0774872c514575ff878f31d096d
OVOS_SHELL_SITE = $(call github,OpenVoiceOS,ovos-shell,$(OVOS_SHELL_VERSION))
OVOS_SHELL_LICENSE = Apache License 2.0

OVOS_SHELL_INSTALL_STAGING = YES
OVOS_SHELL_DEPENDENCIES = host-pkgconf
OVOS_SHELL_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
