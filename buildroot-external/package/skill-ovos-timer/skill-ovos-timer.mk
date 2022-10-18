################################################################################
#
# skill-ovos-timer
#
################################################################################

SKILL_OVOS_TIMER_VERSION = 7cedc9e8c3055bcc212fd5bb2b53b8383382c7e1
SKILL_OVOS_TIMER_SITE = $(call github,OpenVoiceOS,skill-ovos-timer,$(SKILL_OVOS_TIMER_VERSION))
SKILL_OVOS_TIMER_SETUP_TYPE = setuptools
SKILL_OVOS_TIMER_LICENSE_FILES = LICENSE
SKILL_OVOS_TIMER_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
