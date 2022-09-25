################################################################################
#
# skill-date-time
#
################################################################################

SKILL_DATE_TIME_VERSION = 7763a6eb8cfe8b873c1a6cff085d16bc3ac04afe
SKILL_DATE_TIME_SITE = $(call github,OpenVoiceOS,skill-date-time,$(SKILL_DATE_TIME_VERSION))
SKILL_DATE_TIME_SETUP_TYPE = setuptools
SKILL_DATE_TIME_LICENSE_FILES = LICENSE

$(eval $(python-package))
