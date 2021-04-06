################################################################################
#
# python-ovos-skill-installer
#
################################################################################

PYTHON_OVOS_SKILL_INSTALLER_VERSION = 79db45e21bdf06cfa6f93a3dcf6a78cefaea1554
PYTHON_OVOS_SKILL_INSTALLER_SITE = $(call github,OpenVoiceOS,ovos_skill_installer,$(PYTHON_OVOS_SKILL_INSTALLER_VERSION))
PYTHON_OVOS_SKILL_INSTALLER_SETUP_TYPE = setuptools
PYTHON_OVOS_SKILL_INSTALLER_LICENSE_FILES = LICENSE

$(eval $(python-package))
