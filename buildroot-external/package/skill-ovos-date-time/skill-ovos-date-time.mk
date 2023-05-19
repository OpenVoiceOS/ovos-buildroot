################################################################################
#
# skill-ovos-date-time
#
################################################################################

SKILL_OVOS_DATE_TIME_VERSION = a4a531e4d31e4b13aac5ccc8d25962193a91a47e
SKILL_OVOS_DATE_TIME_SITE = $(call github,OpenVoiceOS,skill-ovos-date-time,$(SKILL_OVOS_DATE_TIME_VERSION))
SKILL_OVOS_DATE_TIME_SETUP_TYPE = setuptools
SKILL_OVOS_DATE_TIME_LICENSE_FILES = LICENSE
SKILL_OVOS_DATE_TIME_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
