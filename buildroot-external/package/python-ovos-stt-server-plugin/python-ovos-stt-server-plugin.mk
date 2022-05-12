################################################################################
#
# python-ovos-stt-server-plugin
#
################################################################################

PYTHON_OVOS_STT_SERVER_PLUGIN_VERSION = f3b76321aee87f61aea3f0e3cb04aef831f369c1
PYTHON_OVOS_STT_SERVER_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-stt-server-plugin,$(PYTHON_OVOS_STT_SERVER_PLUGIN_VERSION))
PYTHON_OVOS_STT_SERVER_PLUGIN_SETUP_TYPE = setuptools

$(eval $(python-package))
