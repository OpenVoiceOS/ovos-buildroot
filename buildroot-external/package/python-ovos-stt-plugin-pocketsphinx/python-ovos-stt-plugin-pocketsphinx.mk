################################################################################
#
# python-ovos-stt-plugin-pocketsphinx
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_VERSION = 5294df7bdd21e1319fa3579afdb36458e2a3d24a
PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_SITE = $(call github,OpenVoiceOS,ovos-stt-plugin-pocketsphinx,$(PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_VERSION))
PYTHON_OVOS_STT_PLUGIN_POCKETSPHINX_SETUP_TYPE = setuptools

$(eval $(python-package))
