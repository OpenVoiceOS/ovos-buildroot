################################################################################
#
# ovos-bus-server
#
################################################################################

OVOS_BUS_SERVER_VERSION = 6390bb787fad4660106577891ada6fa935b662d7
OVOS_BUS_SERVER_SITE = $(call github,OpenVoiceOS,ovos-bus-server,$(OVOS_BUS_SERVER_VERSION))
OVOS_BUS_SERVER_LICENSE = Apache License 2.0

OVOS_BUS_SERVER_INSTALL_STAGING = YES
OVOS_BUS_SERVER_DEPENDENCIES = host-pkgconf
OVOS_BUS_SERVER_SUPPORTS_IN_SOURCE_BUILD = NO
OVOS_BUS_SERVER_SUBDIR = server

$(eval $(cmake-package))
