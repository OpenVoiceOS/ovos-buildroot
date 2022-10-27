################################################################################
#
# python-ovos-stt-plugin-pocketsphinx
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_VERSION = c11b940f64af87f95012605e65dfec9722c6afdd
PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-pocketsphinx,$(PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_VERSION))
PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_SETUP_TYPE = setuptools
PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
