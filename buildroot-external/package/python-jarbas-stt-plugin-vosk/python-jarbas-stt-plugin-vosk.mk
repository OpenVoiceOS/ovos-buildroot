################################################################################
#
# python-jarbas-stt-plugin-vosk
#
################################################################################

PYTHON_JARBAS_STT_PLUGIN_VOSK_VERSION = 0.1.3
PYTHON_JARBAS_STT_PLUGIN_VOSK_SOURCE = jarbas-stt-plugin-vosk-$(PYTHON_JARBAS_STT_PLUGIN_VOSK_VERSION).tar.gz
PYTHON_JARBAS_STT_PLUGIN_VOSK_SITE = https://files.pythonhosted.org/packages/c1/82/5a3a041d602c511cd9a611d274b9e8ce38272bb2e03a67c0aff299d7a689
PYTHON_JARBAS_STT_PLUGIN_VOSK_SETUP_TYPE = setuptools

$(eval $(python-package))
