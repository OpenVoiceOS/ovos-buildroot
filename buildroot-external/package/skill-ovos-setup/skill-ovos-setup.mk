################################################################################
#
# skill-ovos-setup
#
################################################################################

SKILL_OVOS_SETUP_VERSION = 713404dbc9a4b594f09a292f7fd5b25f01aea850
SKILL_OVOS_SETUP_SITE = $(call github,OpenVoiceOS,skill-ovos-setup,$(SKILL_OVOS_SETUP_VERSION))
SKILL_OVOS_SETUP_SETUP_TYPE = setuptools
SKILL_OVOS_SETUP_LICENSE_FILES = LICENSE

$(eval $(python-package))
