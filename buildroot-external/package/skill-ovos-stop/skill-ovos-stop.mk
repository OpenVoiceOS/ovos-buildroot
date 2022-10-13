################################################################################
#
# skill-ovos-stop
#
################################################################################

SKILL_OVOS_STOP_VERSION = 8c42181e3b1eac413dfb673cfcd686d4dc7b8a0c
SKILL_OVOS_STOP_SITE = $(call github,OpenVoiceOS,skill-ovos-stop,$(SKILL_OVOS_STOP_VERSION))
SKILL_OVOS_STOP_SETUP_TYPE = setuptools
SKILL_OVOS_STOP_LICENSE_FILES = LICENSE

$(eval $(python-package))
