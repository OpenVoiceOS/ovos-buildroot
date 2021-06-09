################################################################################
#
# mycroft-skill-audio-record
#
################################################################################

MYCROFT_SKILL_AUDIO_RECORD_VERSION = 501a960d7957c83f340c58de4d25301ddb85ea51
MYCROFT_SKILL_AUDIO_RECORD_SITE = git://github.com/MycroftAI/skill-audio-record
MYCROFT_SKILL_AUDIO_RECORD_SITE_METHOD = git
MYCROFT_SKILL_AUDIO_RECORD_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_AUDIO_RECORD_DIRNAME = skill-audio-record.mycroftai

define MYCROFT_SKILL_AUDIO_RECORD_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_AUDIO_RECORD_DIRLOCATION)/$(MYCROFT_SKILL_AUDIO_RECORD_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_AUDIO_RECORD_DIRLOCATION)/$(MYCROFT_SKILL_AUDIO_RECORD_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_AUDIO_RECORD_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_AUDIO_RECORD_DIRLOCATION)/$(MYCROFT_SKILL_AUDIO_RECORD_DIRNAME)
endef

$(eval $(generic-package))
