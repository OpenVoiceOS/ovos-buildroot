################################################################################
#
# python-ovos-ocp-files-plugin
#
################################################################################

PYTHON_OVOS_OCP_FILES_PLUGIN_VERSION = 6a3a9426dfff9666ebb0026519a4bcaae609086b
PYTHON_OVOS_OCP_FILES_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-ocp-files-plugin,$(PYTHON_OVOS_OCP_FILES_PLUGIN_VERSION))
PYTHON_OVOS_OCP_FILES_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_OCP_FILES_PLUGIN_LICENSE_FILES = LICENSE
PYTHON_OVOS_OCP_FILES_PLUGIN_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
