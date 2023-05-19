################################################################################
#
# skill-ovos-naptime
#
################################################################################

SKILL_OVOS_NAPTIME_VERSION = 92ab0cbef48273148c706a1b6f52d1574adb476f
SKILL_OVOS_NAPTIME_SITE = $(call github,OpenVoiceOS,skill-ovos-naptime,$(SKILL_OVOS_NAPTIME_VERSION))
SKILL_OVOS_NAPTIME_SETUP_TYPE = setuptools
SKILL_OVOS_NAPTIME_LICENSE_FILES = LICENSE

$(eval $(python-package))
