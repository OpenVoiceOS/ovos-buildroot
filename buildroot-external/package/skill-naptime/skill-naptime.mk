################################################################################
#
# skill-naptime
#
################################################################################

SKILL_NAPTIME_VERSION = 7a178b1ac7dc438235d09aadeb289a0a19c6aa0a
SKILL_NAPTIME_SITE = $(call github,OpenVoiceOS,ovos-skill-naptime,$(SKILL_NAPTIME_VERSION))
SKILL_NAPTIME_SETUP_TYPE = setuptools
SKILL_NAPTIME_LICENSE_FILES = LICENSE

$(eval $(python-package))
