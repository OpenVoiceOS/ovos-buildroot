################################################################################
#
# mycroft-skill-ip
#
################################################################################

MYCROFT_SKILL_IP_VERSION = 0e836fb98d8113475c808c64bc10424e8436d5ef
MYCROFT_SKILL_IP_SITE = git://github.com/MycroftAI/skill-ip
MYCROFT_SKILL_IP_SITE_METHOD = git
MYCROFT_SKILL_IP_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_IP_DIRNAME = skill-ip.mycroftai

define MYCROFT_SKILL_IP_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_IP_DIRLOCATION)/$(MYCROFT_SKILL_IP_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_IP_DIRLOCATION)/$(MYCROFT_SKILL_IP_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_IP_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_IP_DIRLOCATION)/$(MYCROFT_SKILL_IP_DIRNAME)
endef

$(eval $(generic-package))
