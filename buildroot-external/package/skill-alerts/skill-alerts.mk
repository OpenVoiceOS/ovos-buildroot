################################################################################
#
# skill-alerts
#
################################################################################

SKILL_ALERTS_VERSION = 83c9a717d6829492b9c95485de6ff0acc76ab962
SKILL_ALERTS_SITE = $(call github,OpenVoiceOS,skill-alerts,$(SKILL_ALERTS_VERSION))
SKILL_ALERTS_SETUP_TYPE = setuptools
SKILL_ALERTS_LICENSE_FILES = LICENSE

$(eval $(python-package))
