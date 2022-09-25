################################################################################
#
# skill-ovos-homescreen
#
################################################################################

SKILL_OVOS_HOMESCREEN_VERSION = e6cb87ca46d3f3b0b4125b0072e9c79a2634f2e6
SKILL_OVOS_HOMESCREEN_SITE = $(call github,OpenVoiceOS,skill-ovos-homescreen,$(SKILL_OVOS_HOMESCREEN_VERSION))
SKILL_OVOS_HOMESCREEN_SETUP_TYPE = setuptools
SKILL_OVOS_HOMESCREEN_LICENSE_FILES = LICENSE

$(eval $(python-package))
