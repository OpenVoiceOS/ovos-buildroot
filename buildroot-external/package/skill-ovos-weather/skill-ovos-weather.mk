################################################################################
#
# skill-ovos-weather
#
################################################################################

SKILL_OVOS_WEATHER_VERSION = e275b90fc0738d4677586e207e39bbd84660e857
SKILL_OVOS_WEATHER_SITE = $(call github,OpenVoiceOS,skill-ovos-weather,$(SKILL_OVOS_WEATHER_VERSION))
SKILL_OVOS_WEATHER_SETUP_TYPE = setuptools
SKILL_OVOS_WEATHER_LICENSE_FILES = LICENSE

$(eval $(python-package))
