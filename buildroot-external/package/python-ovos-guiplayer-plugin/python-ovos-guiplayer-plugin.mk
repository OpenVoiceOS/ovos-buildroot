################################################################################
#
# python-ovos-guiplayer-plugin
#
################################################################################

PYTHON_OVOS_GUIPLAYER_PLUGIN_VERSION = 4f9896def4ae4b619a9dd979d9b159a4dbf4fb3b
PYTHON_OVOS_GUIPLAYER_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-guiplayer-plugin,$(PYTHON_OVOS_GUIPLAYER_PLUGIN_VERSION))
PYTHON_OVOS_GUIPLAYER_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_GUIPLAYER_PLUGIN_LICENSE_FILES = LICENSE

$(eval $(python-package))
