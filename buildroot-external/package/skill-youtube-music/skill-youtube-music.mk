################################################################################
#
# skill-youtube-music
#
################################################################################

SKILL_YOUTUBE_MUSIC_VERSION = b883d9bc64f75e890eef4c6530f63a0444c87814
SKILL_YOUTUBE_MUSIC_SITE = $(call github,JarbasSkills,skill-youtube-music,$(SKILL_YOUTUBE_MUSIC_VERSION))
SKILL_YOUTUBE_MUSIC_SETUP_TYPE = setuptools
SKILL_YOUTUBE_MUSIC_LICENSE_FILES = LICENSE

$(eval $(python-package))
