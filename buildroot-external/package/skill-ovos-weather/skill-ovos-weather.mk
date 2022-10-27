################################################################################
#
# skill-ovos-weather
#
################################################################################

SKILL_OVOS_WEATHER_VERSION = 133f659c58331a1322587532c57e6a23f6baa83d
SKILL_OVOS_WEATHER_SITE = $(call github,OpenVoiceOS,skill-ovos-weather,$(SKILL_OVOS_WEATHER_VERSION))
SKILL_OVOS_WEATHER_SETUP_TYPE = setuptools
SKILL_OVOS_WEATHER_LICENSE_FILES = LICENSE

$(eval $(python-package))
