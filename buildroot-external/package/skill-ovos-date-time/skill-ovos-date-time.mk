################################################################################
#
# skill-ovos-date-time
#
################################################################################

SKILL_OVOS_DATE_TIME_VERSION = 6d0250a63beb408a7c25fd5f2c5e4d0d1e859318
SKILL_OVOS_DATE_TIME_SITE = $(call github,OpenVoiceOS,skill-ovos-date-time,$(SKILL_OVOS_DATE_TIME_VERSION))
SKILL_OVOS_DATE_TIME_SETUP_TYPE = setuptools
SKILL_OVOS_DATE_TIME_LICENSE_FILES = LICENSE
SKILL_OVOS_DATE_TIME_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
