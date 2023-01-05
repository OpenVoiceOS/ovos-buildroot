################################################################################
#
# skill-local-music
#
################################################################################

SKILL_LOCAL_MUSIC_VERSION = c03107987c3f2aba23e8933ff0fc93a7217655b9
SKILL_LOCAL_MUSIC_SITE = $(call github,NeonGeckoCom,skill-local_music,$(SKILL_LOCAL_MUSIC_VERSION))
SKILL_LOCAL_MUSIC_SETUP_TYPE = setuptools
SKILL_LOCAL_MUSIC_LICENSE_FILES = LICENSE

$(eval $(python-package))
