################################################################################
#
# skill-ovos-wikipedia
#
################################################################################

SKILL_OVOS_WIKIPEDIA_VERSION = 47e43ef8466f18258cc336ddd0c21b5c09398305
SKILL_OVOS_WIKIPEDIA_SITE = $(call github,OpenVoiceOS,skill-ovos-wikipedia,$(SKILL_OVOS_WIKIPEDIA_VERSION))
SKILL_OVOS_WIKIPEDIA_SETUP_TYPE = setuptools
SKILL_OVOS_WIKIPEDIA_LICENSE_FILES = LICENSE

$(eval $(generic-package))
