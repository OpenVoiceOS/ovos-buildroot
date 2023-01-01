################################################################################
#
# skill-ovos-fallback-unknown
#
################################################################################

SKILL_OVOS_FALLBACK_UNKNOWN_VERSION = 185f029f7777d320fb713e04b11b295c4549e103
SKILL_OVOS_FALLBACK_UNKNOWN_SITE = $(call github,OpenVoiceOS,ovos-skill-fallback-unknown,$(SKILL_OVOS_FALLBACK_UNKNOWN_VERSION))
SKILL_OVOS_FALLBACK_UNKNOWN_SETUP_TYPE = setuptools
SKILL_OVOS_FALLBACK_UNKNOWN_LICENSE_FILES = LICENSE

$(eval $(python-package))
