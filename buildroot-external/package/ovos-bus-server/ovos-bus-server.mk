################################################################################
#
# ovos-bus-server
#
################################################################################

OVOS_BUS_SERVER_VERSION = 2bd52c9703cf7fcf8d9730f1586cc1f005b459cd
OVOS_BUS_SERVER_SITE = $(call github,OpenVoiceOS,ovos-bus-server,$(OVOS_BUS_SERVER_VERSION))
OVOS_BUS_SERVER_LICENSE = Apache License 2.0

OVOS_BUS_SERVER_INSTALL_STAGING = YES
OVOS_BUS_SERVER_DEPENDENCIES = host-pkgconf
OVOS_BUS_SERVER_SUPPORTS_IN_SOURCE_BUILD = NO
OVOS_BUS_SERVER_SUBDIR = server

$(eval $(cmake-package))
