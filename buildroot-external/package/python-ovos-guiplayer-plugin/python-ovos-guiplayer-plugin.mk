################################################################################
#
# python-ovos-guiplayer-plugin
#
################################################################################

PYTHON_OVOS_GUIPLAYER_PLUGIN_VERSION = f6b0dc8082672f6c5f092be7ffe2d0f4b0520882
PYTHON_OVOS_GUIPLAYER_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-guiplayer-plugin,$(PYTHON_OVOS_GUIPLAYER_PLUGIN_VERSION))
PYTHON_OVOS_GUIPLAYER_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_GUIPLAYER_PLUGIN_LICENSE_FILES = LICENSE

$(eval $(python-package))
