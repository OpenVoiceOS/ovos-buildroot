################################################################################
#
# skill-ovos-personal
#
################################################################################

SKILL_OVOS_PERSONAL_VERSION = e4f04baee00b3b137ed317e1801e41f6d885cc91
SKILL_OVOS_PERSONAL_SITE = $(call github,OpenVoiceOS,ovos-skill-personal,$(SKILL_OVOS_PERSONAL_VERSION))
SKILL_OVOS_PERSONAL_SETUP_TYPE = setuptools
SKILL_OVOS_PERSONAL_LICENSE_FILES = LICENSE

$(eval $(python-package))
