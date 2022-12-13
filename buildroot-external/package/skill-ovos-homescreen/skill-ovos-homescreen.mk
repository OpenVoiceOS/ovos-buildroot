################################################################################
#
# skill-ovos-homescreen
#
################################################################################

SKILL_OVOS_HOMESCREEN_VERSION = a5373203b6266f309a3aee9f7c1528c5a25e8447
SKILL_OVOS_HOMESCREEN_SITE = $(call github,OpenVoiceOS,skill-ovos-homescreen,$(SKILL_OVOS_HOMESCREEN_VERSION))
SKILL_OVOS_HOMESCREEN_SETUP_TYPE = setuptools
SKILL_OVOS_HOMESCREEN_LICENSE_FILES = LICENSE
SKILL_OVOS_HOMESCREEN_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
