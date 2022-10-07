################################################################################
#
# skill-ovos-fallback-unknown
#
################################################################################

SKILL_OVOS_FALLBACK_UNKNOWN_VERSION = 2ce227adf319512ecd67897fb56f832d8656b981
SKILL_OVOS_FALLBACK_UNKNOWN_SITE = $(call github,OpenVoiceOS,ovos-skill-fallback-unknown,$(SKILL_OVOS_FALLBACK_UNKNOWN_VERSION))
SKILL_OVOS_FALLBACK_UNKNOWN_SETUP_TYPE = setuptools
SKILL_OVOS_FALLBACK_UNKNOWN_LICENSE_FILES = LICENSE

$(eval $(python-package))
