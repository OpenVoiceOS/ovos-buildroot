################################################################################
#
# skill-ovos-ddg
#
################################################################################

SKILL_OVOS_DDG_VERSION = 76dd835225ba69c4f6f91edc95c47d142829ba92
SKILL_OVOS_DDG_SITE = $(call github,OpenVoiceOS,skill-ovos-ddg,$(SKILL_OVOS_DDG_VERSION))
SKILL_OVOS_DDG_SETUP_TYPE = setuptools
SKILL_OVOS_DDG_LICENSE_FILES = LICENSE

$(eval $(python-package))
