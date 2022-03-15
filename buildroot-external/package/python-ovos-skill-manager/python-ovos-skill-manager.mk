################################################################################
#
# python-ovos-skill-manager
#
################################################################################

PYTHON_OVOS_SKILL_MANAGER_VERSION = 067385a42b1cf2dff87b4775fd34886663d137bd
PYTHON_OVOS_SKILL_MANAGER_SITE = $(call github,OpenVoiceOS,ovos_skill_manager,$(PYTHON_OVOS_SKILL_MANAGER_VERSION))
PYTHON_OVOS_SKILL_MANAGER_SETUP_TYPE = setuptools
PYTHON_OVOS_SKILL_MANAGER_LICENSE_FILES = LICENSE

$(eval $(python-package))
