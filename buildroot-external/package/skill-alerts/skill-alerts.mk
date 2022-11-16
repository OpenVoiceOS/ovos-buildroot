################################################################################
#
# skill-alerts
#
################################################################################

SKILL_ALERTS_VERSION = fa8b142fdd485a3c5cdb3757d10ca1b4ba019eb9
SKILL_ALERTS_SITE = $(call github,NeonGeckoCom,skill-alerts,$(SKILL_ALERTS_VERSION))
SKILL_ALERTS_SETUP_TYPE = setuptools
SKILL_ALERTS_LICENSE_FILES = LICENSE

$(eval $(python-package))
