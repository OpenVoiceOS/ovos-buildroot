################################################################################
#
# python-ovos-guiplayer-plugin
#
################################################################################

PYTHON_OVOS_GUIPLAYER_PLUGIN_VERSION = e265477980aa77eeee7d7cf00567753b7b612223
PYTHON_OVOS_GUIPLAYER_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-guiplayer-plugin,$(PYTHON_OVOS_GUIPLAYER_PLUGIN_VERSION))
PYTHON_OVOS_GUIPLAYER_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_GUIPLAYER_PLUGIN_LICENSE_FILES = LICENSE

$(eval $(python-package))
