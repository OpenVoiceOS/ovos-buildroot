################################################################################
#
# skill-ovos-wolfie
#
################################################################################

SKILL_OVOS_WOLFIE_VERSION = 6c2a82cdeedc5e963df35201f833e67dc8badfba
SKILL_OVOS_WOLFIE_SITE = $(call github,OpenVoiceOS,skill-ovos-wolfie,$(SKILL_OVOS_WOLFIE_VERSION))
SKILL_OVOS_WOLFIE_SETUP_TYPE = setuptools
SKILL_OVOS_WOLFIE_LICENSE_FILES = LICENSE

$(eval $(python-package))
