################################################################################
#
# skill-camera
#
################################################################################

SKILL_CAMERA_VERSION = d860c322f94775e4aee327279141982d379ec899
SKILL_CAMERA_SITE = $(call github,OpenVoiceOS,skill-camera,$(SKILL_CAMERA_VERSION))
SKILL_CAMERA_SETUP_TYPE = setuptools
SKILL_CAMERA_LICENSE_FILES = LICENSE

$(eval $(python-package))
