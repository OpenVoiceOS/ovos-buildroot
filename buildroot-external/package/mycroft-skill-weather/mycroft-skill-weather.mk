################################################################################
#
# mycroft-skill-weather
#
################################################################################

MYCROFT_SKILL_WEATHER_VERSION = 541490bce01576e2eef5650440fa1103fccdaaeb
MYCROFT_SKILL_WEATHER_SITE = https://github.com/OpenVoiceOS/skill-weather
MYCROFT_SKILL_WEATHER_SITE_METHOD = git
MYCROFT_SKILL_WEATHER_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_WEATHER_DIRNAME = skill-weather.openvoiceos

define MYCROFT_SKILL_WEATHER_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_WEATHER_DIRLOCATION)/$(MYCROFT_SKILL_WEATHER_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_WEATHER_DIRLOCATION)/$(MYCROFT_SKILL_WEATHER_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_WEATHER_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_WEATHER_DIRLOCATION)/$(MYCROFT_SKILL_WEATHER_DIRNAME)
endef

$(eval $(generic-package))
