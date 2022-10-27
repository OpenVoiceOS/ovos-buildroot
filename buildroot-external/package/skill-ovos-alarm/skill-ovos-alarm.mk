################################################################################
#
# skill-ovos-alarm
#
################################################################################

SKILL_OVOS_ALARM_VERSION = 6c14d41903227be490b5249ef464585b7694e4c1
SKILL_OVOS_ALARM_SITE = $(call github,OpenVoiceOS,skill-ovos-alarm,$(SKILL_OVOS_ALARM_VERSION))
SKILL_OVOS_ALARM_SETUP_TYPE = setuptools
SKILL_OVOS_ALARM_LICENSE_FILES = LICENSE

$(eval $(python-package))
