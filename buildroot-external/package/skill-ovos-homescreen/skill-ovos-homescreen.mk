################################################################################
#
# skill-ovos-homescreen
#
################################################################################

SKILL_OVOS_HOMESCREEN_VERSION = 1f9e6377077821b1f589099d3bc351b8ac3d1695
SKILL_OVOS_HOMESCREEN_SITE = $(call github,OpenVoiceOS,skill-ovos-homescreen,$(SKILL_OVOS_HOMESCREEN_VERSION))
SKILL_OVOS_HOMESCREEN_SETUP_TYPE = setuptools
SKILL_OVOS_HOMESCREEN_LICENSE_FILES = LICENSE
SKILL_OVOS_HOMESCREEN_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
