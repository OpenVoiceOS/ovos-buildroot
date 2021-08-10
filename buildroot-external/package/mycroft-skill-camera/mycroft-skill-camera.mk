################################################################################
#
# mycroft-skill-camera
#
################################################################################

MYCROFT_SKILL_CAMERA_VERSION = a52e306f99d6a4468f3998ae85196f52bbcdad73
MYCROFT_SKILL_CAMERA_SITE = git://github.com/MycroftAI/skill-camera
MYCROFT_SKILL_CAMERA_SITE_METHOD = git
MYCROFT_SKILL_CAMERA_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_CAMERA_DIRNAME = skill-camera.mycroftai

define MYCROFT_SKILL_CAMERA_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_CAMERA_DIRLOCATION)/$(MYCROFT_SKILL_CAMERA_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_CAMERA_DIRLOCATION)/$(MYCROFT_SKILL_CAMERA_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_CAMERA_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_CAMERA_DIRLOCATION)/$(MYCROFT_SKILL_CAMERA_DIRNAME)
endef

$(eval $(generic-package))
