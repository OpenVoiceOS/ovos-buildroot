################################################################################
#
# skill-ovos-ddg
#
################################################################################

SKILL_OVOS_DDG_VERSION = 6209146d4714dfa6a5588a9bcc10df16d5cbb373
SKILL_OVOS_DDG_SITE = $(call github,OpenVoiceOS,skill-ovos-ddg,$(SKILL_OVOS_DDG_VERSION))
SKILL_OVOS_DDG_SETUP_TYPE = setuptools
SKILL_OVOS_DDG_LICENSE_FILES = LICENSE

$(eval $(python-package))
