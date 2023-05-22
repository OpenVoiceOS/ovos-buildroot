################################################################################
#
# skill-ovos-weather
#
################################################################################

SKILL_OVOS_WEATHER_VERSION = 184c913504c48e1fa4cfe8f5070cb2c45f85114a
SKILL_OVOS_WEATHER_SITE = $(call github,OpenVoiceOS,skill-ovos-weather,$(SKILL_OVOS_WEATHER_VERSION))
SKILL_OVOS_WEATHER_SETUP_TYPE = setuptools
SKILL_OVOS_WEATHER_LICENSE_FILES = LICENSE

$(eval $(python-package))
