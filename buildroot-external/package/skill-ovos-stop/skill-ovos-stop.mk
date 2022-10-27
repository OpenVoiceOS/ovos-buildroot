################################################################################
#
# skill-ovos-stop
#
################################################################################

SKILL_OVOS_STOP_VERSION = cd940b2323533b64465a72b8935e322fce303719
SKILL_OVOS_STOP_SITE = $(call github,OpenVoiceOS,skill-ovos-stop,$(SKILL_OVOS_STOP_VERSION))
SKILL_OVOS_STOP_SETUP_TYPE = setuptools
SKILL_OVOS_STOP_LICENSE_FILES = LICENSE

$(eval $(python-package))
