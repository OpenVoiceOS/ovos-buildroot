################################################################################
#
# skill-ovos-setup
#
################################################################################

SKILL_OVOS_SETUP_VERSION = 8d4c94183825389b8c7ecc80eb84f54689bedf5b
SKILL_OVOS_SETUP_SITE = $(call github,OpenVoiceOS,skill-ovos-setup,$(SKILL_OVOS_SETUP_VERSION))
SKILL_OVOS_SETUP_SETUP_TYPE = setuptools
SKILL_OVOS_SETUP_LICENSE_FILES = LICENSE

$(eval $(python-package))
