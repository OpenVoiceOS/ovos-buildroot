################################################################################
#
# skill-ovos-homescreen
#
################################################################################

SKILL_OVOS_HOMESCREEN_VERSION = 7cee3bf265fd267e68aefe75772e8391792f1038
SKILL_OVOS_HOMESCREEN_SITE = $(call github,OpenVoiceOS,skill-ovos-homescreen,$(SKILL_OVOS_HOMESCREEN_VERSION))
SKILL_OVOS_HOMESCREEN_SETUP_TYPE = setuptools
SKILL_OVOS_HOMESCREEN_LICENSE_FILES = LICENSE

$(eval $(python-package))
