################################################################################
#
# python-ovos-skill-manager
#
################################################################################

PYTHON_OVOS_SKILL_MANAGER_VERSION = 9f3f4f7c941546d40eb5a5ff88d7bdd0c1a11236
PYTHON_OVOS_SKILL_MANAGER_SITE = $(call github,OpenVoiceOS,ovos_skill_manager,$(PYTHON_OVOS_SKILL_MANAGER_VERSION))
PYTHON_OVOS_SKILL_MANAGER_SETUP_TYPE = setuptools
PYTHON_OVOS_SKILL_MANAGER_LICENSE_FILES = LICENSE

$(eval $(python-package))
