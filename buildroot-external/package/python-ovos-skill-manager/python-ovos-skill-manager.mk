################################################################################
#
# python-ovos-skill-manager
#
################################################################################

PYTHON_OVOS_SKILL_MANAGER_VERSION = 20b9275cd929b250dd7e5c9b4700cb41b0f07c89
PYTHON_OVOS_SKILL_MANAGER_SITE = $(call github,OpenVoiceOS,ovos_skill_manager,$(PYTHON_OVOS_SKILL_MANAGER_VERSION))
PYTHON_OVOS_SKILL_MANAGER_SETUP_TYPE = setuptools
PYTHON_OVOS_SKILL_MANAGER_LICENSE_FILES = LICENSE

$(eval $(python-package))
