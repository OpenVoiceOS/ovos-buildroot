################################################################################
#
# skill-ovos-info
#
################################################################################

SKILL_OVOS_INFO_VERSION = acab00e38d5492aca13b2072114f630791b5ee01
SKILL_OVOS_INFO_SITE = $(call github,OpenVoiceOS,ovos-skills-info,$(SKILL_OVOS_INFO_VERSION))
SKILL_OVOS_INFO_SETUP_TYPE = setuptools
SKILL_OVOS_INFO_LICENSE_FILES = LICENSE

$(eval $(python-package))
