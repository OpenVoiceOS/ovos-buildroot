################################################################################
#
# skill-wolfie
#
################################################################################

SKILL_WOLFIE_VERSION = c5ff51a0c5390cbf579293f74e30028061453344
SKILL_WOLFIE_SITE = $(call github,OpenVoiceOS,skill-wolfie,$(SKILL_WOLFIE_VERSION))
SKILL_WOLFIE_SETUP_TYPE = setuptools
SKILL_WOLFIE_LICENSE_FILES = LICENSE

$(eval $(python-package))
