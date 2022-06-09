################################################################################
#
# mycroft-skill-weather
#
################################################################################

MYCROFT_SKILL_WEATHER_VERSION = 9748286ff43cbe5bbf8c8ab457d58ce9668cd46e
MYCROFT_SKILL_WEATHER_SITE = https://github.com/OpenVoiceOS/skill-ovos-weather
MYCROFT_SKILL_WEATHER_SITE_METHOD = git
MYCROFT_SKILL_WEATHER_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_WEATHER_DIRNAME = skill-ovos-weather.openvoiceos

define MYCROFT_SKILL_WEATHER_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_WEATHER_DIRLOCATION)/$(MYCROFT_SKILL_WEATHER_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_WEATHER_DIRLOCATION)/$(MYCROFT_SKILL_WEATHER_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_WEATHER_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_WEATHER_DIRLOCATION)/$(MYCROFT_SKILL_WEATHER_DIRNAME)
endef

$(eval $(generic-package))
