################################################################################
#
# skill-ovos-alarm
#
################################################################################

SKILL_OVOS_ALARM_VERSION = a56428291b706f46add9828cb5f7f29ac41a08e1
SKILL_OVOS_ALARM_SITE = $(call github,OpenVoiceOS,skill-ovos-alarm,$(SKILL_OVOS_ALARM_VERSION))
SKILL_OVOS_ALARM_SETUP_TYPE = setuptools
SKILL_OVOS_ALARM_LICENSE_FILES = LICENSE

$(eval $(python-package))
