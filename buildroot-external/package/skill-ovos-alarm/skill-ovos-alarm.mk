################################################################################
#
# skill-ovos-alarm
#
################################################################################

SKILL_OVOS_ALARM_VERSION = d3fb437d41ae63d35f4fee55184f47b9573b04cc
SKILL_OVOS_ALARM_SITE = $(call github,OpenVoiceOS,skill-ovos-alarm,$(SKILL_OVOS_ALARM_VERSION))
SKILL_OVOS_ALARM_SETUP_TYPE = setuptools
SKILL_OVOS_ALARM_LICENSE_FILES = LICENSE

$(eval $(python-package))
