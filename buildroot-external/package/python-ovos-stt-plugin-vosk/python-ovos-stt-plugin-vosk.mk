################################################################################
#
# python-ovos-stt-plugin-vosk
#
################################################################################

PYTHON_OVOS_STT_PLUGIN_VOSK_VERSION = 0.1.0
PYTHON_OVOS_STT_PLUGIN_VOSK_SOURCE = ovos-stt-plugin-vosk-$(PYTHON_OVOS_STT_PLUGIN_VOSK_VERSION).tar.gz
PYTHON_OVOS_STT_PLUGIN_VOSK_SITE = https://files.pythonhosted.org/packages/2c/fa/fd30cced0c7defd817c1da7234488ad0f4233fb4500d7df60d6930921f07
PYTHON_OVOS_STT_PLUGIN_VOSK_SETUP_TYPE = setuptools

$(eval $(python-package))
