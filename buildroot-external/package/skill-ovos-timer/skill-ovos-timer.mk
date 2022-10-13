################################################################################
#
# skill-ovos-timer
#
################################################################################

SKILL_OVOS_TIMER_VERSION = acc876308316f017bbcab21f77c4bae5b61c5ea7
SKILL_OVOS_TIMER_SITE = $(call github,OpenVoiceOS,skill-ovos-timer,$(SKILL_OVOS_TIMER_VERSION))
SKILL_OVOS_TIMER_SETUP_TYPE = setuptools
SKILL_OVOS_TIMER_LICENSE_FILES = LICENSE

$(eval $(python-package))
