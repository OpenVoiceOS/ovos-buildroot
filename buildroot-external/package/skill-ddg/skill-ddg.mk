################################################################################
#
# skill-ddg
#
################################################################################

SKILL_DDG_VERSION = 72dc55998fd7d2817259f2d757fd0f7e5b9b14e1
SKILL_DDG_SITE = $(call github,OpenVoiceOS,skill-ddg,$(SKILL_DDG_VERSION))
SKILL_DDG_SETUP_TYPE = setuptools
SKILL_DDG_LICENSE_FILES = LICENSE

$(eval $(python-package))
