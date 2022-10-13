################################################################################
#
# skill-ovos-setup
#
################################################################################

SKILL_OVOS_SETUP_VERSION = 038543831ec3a38a4d7701f99bca63e55eb80043
SKILL_OVOS_SETUP_SITE = $(call github,OpenVoiceOS,skill-ovos-setup,$(SKILL_OVOS_SETUP_VERSION))
SKILL_OVOS_SETUP_SETUP_TYPE = setuptools
SKILL_OVOS_SETUP_LICENSE_FILES = LICENSE

$(eval $(python-package))
