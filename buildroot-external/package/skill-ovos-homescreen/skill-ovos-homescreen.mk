################################################################################
#
# skill-ovos-homescreen
#
################################################################################

SKILL_OVOS_HOMESCREEN_VERSION = 3f6e8662bc0efbbfd608344a412a0a2df5a2ab3b
SKILL_OVOS_HOMESCREEN_SITE = $(call github,OpenVoiceOS,skill-ovos-homescreen,$(SKILL_OVOS_HOMESCREEN_VERSION))
SKILL_OVOS_HOMESCREEN_SETUP_TYPE = setuptools
SKILL_OVOS_HOMESCREEN_LICENSE_FILES = LICENSE
SKILL_OVOS_HOMESCREEN_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
