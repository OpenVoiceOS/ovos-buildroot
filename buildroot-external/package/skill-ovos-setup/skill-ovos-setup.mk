################################################################################
#
# skill-ovos-setup
#
################################################################################

SKILL_OVOS_SETUP_VERSION = 07895ec93bb72b6a32c90a90b50ae6ba57898414
SKILL_OVOS_SETUP_SITE = $(call github,OpenVoiceOS,skill-ovos-setup,$(SKILL_OVOS_SETUP_VERSION))
SKILL_OVOS_SETUP_SETUP_TYPE = setuptools
SKILL_OVOS_SETUP_LICENSE_FILES = LICENSE

$(eval $(python-package))
