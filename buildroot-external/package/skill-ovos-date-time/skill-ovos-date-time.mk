################################################################################
#
# skill-ovos-date-time
#
################################################################################

SKILL_OVOS_DATE_TIME_VERSION = 824b271a6722e016a8ffc80111b595138abb91ff
SKILL_OVOS_DATE_TIME_SITE = $(call github,OpenVoiceOS,skill-ovos-date-time,$(SKILL_OVOS_DATE_TIME_VERSION))
SKILL_OVOS_DATE_TIME_SETUP_TYPE = setuptools
SKILL_OVOS_DATE_TIME_LICENSE_FILES = LICENSE
SKILL_OVOS_DATE_TIME_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
