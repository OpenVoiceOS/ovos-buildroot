################################################################################
#
# skill-ovos-timer
#
################################################################################

SKILL_OVOS_TIMER_VERSION = 24c38ec3d6744d9fffed9b581d90d62188824310
SKILL_OVOS_TIMER_SITE = $(call github,OpenVoiceOS,skill-ovos-timer,$(SKILL_OVOS_TIMER_VERSION))
SKILL_OVOS_TIMER_SETUP_TYPE = setuptools
SKILL_OVOS_TIMER_LICENSE_FILES = LICENSE
SKILL_OVOS_TIMER_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
