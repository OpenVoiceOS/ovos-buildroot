################################################################################
#
# python-ovos-skill-manager
#
################################################################################

PYTHON_OVOS_SKILL_MANAGER_VERSION = f49bfb8bd69257feaa6e495dee8d6bc8a4c912c9
PYTHON_OVOS_SKILL_MANAGER_SITE = $(call github,OpenVoiceOS,ovos_skill_manager,$(PYTHON_OVOS_SKILL_MANAGER_VERSION))
PYTHON_OVOS_SKILL_MANAGER_SETUP_TYPE = setuptools
PYTHON_OVOS_SKILL_MANAGER_LICENSE_FILES = LICENSE

$(eval $(python-package))
