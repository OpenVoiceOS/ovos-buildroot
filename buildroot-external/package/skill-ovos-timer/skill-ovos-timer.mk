################################################################################
#
# skill-ovos-timer
#
################################################################################

SKILL_OVOS_TIMER_VERSION = 6d0d4df1678cb956d4b36f42b3783f997a723b78
SKILL_OVOS_TIMER_SITE = $(call github,OpenVoiceOS,skill-ovos-timer,$(SKILL_OVOS_TIMER_VERSION))
SKILL_OVOS_TIMER_SETUP_TYPE = setuptools
SKILL_OVOS_TIMER_LICENSE_FILES = LICENSE

$(eval $(python-package))
