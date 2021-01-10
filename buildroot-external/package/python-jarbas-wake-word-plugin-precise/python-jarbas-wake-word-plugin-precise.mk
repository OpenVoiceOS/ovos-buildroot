################################################################################
#
# python-jarbas-wake-word-plugin-precise
#
################################################################################

PYTHON_JARBAS_WAKE_WORD_PLUGIN_PRECISE_VERSION = ad3ced5e4fec11530fc4d065bd446c689e39987a
PYTHON_JARBAS_WAKE_WORD_PLUGIN_PRECISE_SITE = $(call github,JarbasLingua,jarbas-wake-word-plugin-precise,$(PYTHON_JARBAS_WAKE_WORD_PLUGIN_PRECISE_VERSION))
PYTHON_JARBAS_WAKE_WORD_PLUGIN_PRECISE_SETUP_TYPE = setuptools
PYTHON_JARBAS_WAKE_WORD_PLUGIN_PRECISE_LICENSE_FILES = LICENSE

$(eval $(python-package))
