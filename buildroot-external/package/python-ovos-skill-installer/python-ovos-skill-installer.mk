################################################################################
#
# python-ovos-skill-installer
#
################################################################################

PYTHON_OVOS_SKILL_INSTALLER_VERSION = c222dcf46ad36ed3c07ce824f59d123e3abec3dc
PYTHON_OVOS_SKILL_INSTALLER_SITE = $(call github,OpenVoiceOS,ovos_skill_installer,$(PYTHON_OVOS_SKILL_INSTALLER_VERSION))
PYTHON_OVOS_SKILL_INSTALLER_SETUP_TYPE = setuptools
PYTHON_OVOS_SKILL_INSTALLER_LICENSE_FILES = LICENSE

$(eval $(python-package))
