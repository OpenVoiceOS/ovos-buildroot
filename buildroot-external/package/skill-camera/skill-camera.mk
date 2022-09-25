################################################################################
#
# skill-camera
#
################################################################################

SKILL_CAMERA_VERSION = bcbe951fe8c452495d2b588a75f5477899cde4cc
SKILL_CAMERA_SITE = $(call github,OpenVoiceOS,skill-camera,$(SKILL_CAMERA_VERSION))
SKILL_CAMERA_SETUP_TYPE = setuptools
SKILL_CAMERA_LICENSE_FILES = LICENSE

$(eval $(python-package))
