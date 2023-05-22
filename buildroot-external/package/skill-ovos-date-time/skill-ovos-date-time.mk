################################################################################
#
# skill-ovos-date-time
#
################################################################################

SKILL_OVOS_DATE_TIME_VERSION = 4624ed04fd7b547d4da03dbe2dbffb7f63b0e72e
SKILL_OVOS_DATE_TIME_SITE = $(call github,OpenVoiceOS,skill-ovos-date-time,$(SKILL_OVOS_DATE_TIME_VERSION))
SKILL_OVOS_DATE_TIME_SETUP_TYPE = setuptools
SKILL_OVOS_DATE_TIME_LICENSE_FILES = LICENSE
SKILL_OVOS_DATE_TIME_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
