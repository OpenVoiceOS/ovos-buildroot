################################################################################
#
# skill-ovos-wolfie
#
################################################################################

SKILL_OVOS_WOLFIE_VERSION = 1e4af2fa0735f88d19fca917c7130a0995d17fc7
SKILL_OVOS_WOLFIE_SITE = $(call github,OpenVoiceOS,skill-ovos-wolfie,$(SKILL_OVOS_WOLFIE_VERSION))
SKILL_OVOS_WOLFIE_SETUP_TYPE = setuptools
SKILL_OVOS_WOLFIE_LICENSE_FILES = LICENSE

$(eval $(python-package))
