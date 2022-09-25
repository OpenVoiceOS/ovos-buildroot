################################################################################
#
# skill-ovos-weather
#
################################################################################

SKILL_OVOS_WEATHER_VERSION = 114d7753a495d05a28a75199e97e42f93d610a95
SKILL_OVOS_WEATHER_SITE = $(call github,OpenVoiceOS,skill-ovos-weather,$(SKILL_OVOS_WEATHER_VERSION))
SKILL_OVOS_WEATHER_SETUP_TYPE = setuptools
SKILL_OVOS_WEATHER_LICENSE_FILES = LICENSE

$(eval $(python-package))
