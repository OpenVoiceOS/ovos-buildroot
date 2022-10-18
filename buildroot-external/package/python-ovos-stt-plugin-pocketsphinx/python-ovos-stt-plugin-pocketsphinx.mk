################################################################################
#
# python-ovos-stt-plugin-pocketsphinx
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_VERSION = 2d303d2537a7ac8da21fc41e882ae8f0ff9a8c32
PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-pocketsphinx,$(PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_VERSION))
PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_SETUP_TYPE = setuptools
PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
