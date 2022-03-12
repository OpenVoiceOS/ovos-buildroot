################################################################################
#
# mycroft-skill-youtube-music
#
################################################################################

MYCROFT_SKILL_YOUTUBE_MUSIC_VERSION = 85e0cace9e8666aeb3317865802473f78010869c
MYCROFT_SKILL_YOUTUBE_MUSIC_SITE = https://github.com/JarbasSkills/skill-youtube-music
MYCROFT_SKILL_YOUTUBE_MUSIC_SITE_METHOD = git
MYCROFT_SKILL_YOUTUBE_MUSIC_DIRLOCATION = home/mycroft/.local/share/mycroft/skills
MYCROFT_SKILL_YOUTUBE_MUSIC_DIRNAME = skill-youtube-music.jarbasskills

define MYCROFT_SKILL_YOUTUBE_MUSIC_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(MYCROFT_SKILL_YOUTUBE_MUSIC_DIRLOCATION)/$(MYCROFT_SKILL_YOUTUBE_MUSIC_DIRNAME)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(MYCROFT_SKILL_YOUTUBE_MUSIC_DIRLOCATION)/$(MYCROFT_SKILL_YOUTUBE_MUSIC_DIRNAME)
	cp -dpfr $(MYCROFT_SKILL_YOUTUBE_MUSIC_DL_DIR)/git/.git* \
		$(TARGET_DIR)/$(MYCROFT_SKILL_YOUTUBE_MUSIC_DIRLOCATION)/$(MYCROFT_SKILL_YOUTUBE_MUSIC_DIRNAME)
endef

$(eval $(generic-package))
