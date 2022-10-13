################################################################################
#
# skill-ovos-naptime
#
################################################################################

SKILL_OVOS_NAPTIME_VERSION = b78703d45f9035f3741d849928be30a67b178d51
SKILL_OVOS_NAPTIME_SITE = $(call github,OpenVoiceOS,skill-ovos-naptime,$(SKILL_OVOS_NAPTIME_VERSION))
SKILL_OVOS_NAPTIME_SETUP_TYPE = setuptools
SKILL_OVOS_NAPTIME_LICENSE_FILES = LICENSE

$(eval $(python-package))
