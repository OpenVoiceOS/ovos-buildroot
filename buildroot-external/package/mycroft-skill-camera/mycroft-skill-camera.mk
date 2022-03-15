################################################################################
#
# mycroft-skill-camera
#
################################################################################

MYCROFT_SKILL_CAMERA_VERSION = f7409e01f0b4e05e12e18e989dfdd1ae5dea099d
MYCROFT_SKILL_CAMERA_SITE = https://github.com/OpenVoiceOS/skill-camera
MYCROFT_SKILL_CAMERA_SITE_METHOD = git
MYCROFT_SKILL_CAMERA_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_CAMERA_DIRNAME = skill-camera.openvoiceos

define MYCROFT_SKILL_CAMERA_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_CAMERA_DIRLOCATION)/$(MYCROFT_SKILL_CAMERA_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_CAMERA_DIRLOCATION)/$(MYCROFT_SKILL_CAMERA_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_CAMERA_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_CAMERA_DIRLOCATION)/$(MYCROFT_SKILL_CAMERA_DIRNAME)
endef

$(eval $(generic-package))
