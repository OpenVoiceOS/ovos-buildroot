################################################################################
#
# python-ovos-skill-manager
#
################################################################################

PYTHON_OVOS_SKILL_MANAGER_VERSION = da4c5fb16817799cc74426494fe283dcb399f542
PYTHON_OVOS_SKILL_MANAGER_SITE = $(call github,OpenVoiceOS,ovos_skill_manager,$(PYTHON_OVOS_SKILL_MANAGER_VERSION))
PYTHON_OVOS_SKILL_MANAGER_SETUP_TYPE = setuptools
PYTHON_OVOS_SKILL_MANAGER_LICENSE_FILES = LICENSE

$(eval $(python-package))
