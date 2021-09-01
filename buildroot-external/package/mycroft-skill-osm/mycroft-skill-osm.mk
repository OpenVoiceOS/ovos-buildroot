################################################################################
#
# mycroft-skill-osm
#
################################################################################

MYCROFT_SKILL_OSM_VERSION = eaf8356e48afd6299136fe5b6fdc43665043443a
MYCROFT_SKILL_OSM_SITE = git://github.com/OpenVoiceOS/skill-osm
MYCROFT_SKILL_OSM_SITE_METHOD = git
MYCROFT_SKILL_OSM_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_OSM_DIRNAME = skill-osm.openvoiceos

define MYCROFT_SKILL_OSM_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_OSM_DIRLOCATION)/$(MYCROFT_SKILL_OSM_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_OSM_DIRLOCATION)/$(MYCROFT_SKILL_OSM_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_OSM_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_OSM_DIRLOCATION)/$(MYCROFT_SKILL_OSM_DIRNAME)
endef

$(eval $(generic-package))
