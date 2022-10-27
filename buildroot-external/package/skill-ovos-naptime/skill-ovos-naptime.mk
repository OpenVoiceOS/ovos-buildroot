################################################################################
#
# skill-ovos-naptime
#
################################################################################

SKILL_OVOS_NAPTIME_VERSION = b43ebb000da929833702d42dea7711ef9861e2ff
SKILL_OVOS_NAPTIME_SITE = $(call github,OpenVoiceOS,skill-ovos-naptime,$(SKILL_OVOS_NAPTIME_VERSION))
SKILL_OVOS_NAPTIME_SETUP_TYPE = setuptools
SKILL_OVOS_NAPTIME_LICENSE_FILES = LICENSE

$(eval $(python-package))
