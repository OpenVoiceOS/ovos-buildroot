################################################################################
#
# skill-ovos-personal
#
################################################################################

SKILL_OVOS_PERSONAL_VERSION = 7ca20a6e9319eb37f4caacdf2589fc1568b783d3
SKILL_OVOS_PERSONAL_SITE = $(call github,OpenVoiceOS,ovos-skill-personal,$(SKILL_OVOS_PERSONAL_VERSION))
SKILL_OVOS_PERSONAL_SETUP_TYPE = setuptools
SKILL_OVOS_PERSONAL_LICENSE_FILES = LICENSE
SKILL_OVOS_PERSONAL_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
