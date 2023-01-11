################################################################################
#
# python-ovos-ocp-files-plugin
#
################################################################################

PYTHON_OVOS_OCP_FILES_PLUGIN_VERSION = 145cd788eae1f3aaeb214f7a3dda91229c0c5837
PYTHON_OVOS_OCP_FILES_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-ocp-files-plugin,$(PYTHON_OVOS_OCP_FILES_PLUGIN_VERSION))
PYTHON_OVOS_OCP_FILES_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_OCP_FILES_PLUGIN_LICENSE_FILES = LICENSE
PYTHON_OVOS_OCP_FILES_PLUGIN_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
