################################################################################
#
# skill-ovos-date-time
#
################################################################################

SKILL_OVOS_DATE_TIME_VERSION = 0c3c65d291966df82b0f50443abb98ea8bc3d93d
SKILL_OVOS_DATE_TIME_SITE = $(call github,OpenVoiceOS,skill-ovos-date-time,$(SKILL_OVOS_DATE_TIME_VERSION))
SKILL_OVOS_DATE_TIME_SETUP_TYPE = setuptools
SKILL_OVOS_DATE_TIME_LICENSE_FILES = LICENSE
SKILL_OVOS_DATE_TIME_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
