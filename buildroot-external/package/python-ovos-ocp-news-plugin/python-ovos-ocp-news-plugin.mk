################################################################################
#
# python-ovos-ocp-news-plugin
#
################################################################################

PYTHON_OVOS_OCP_NEWS_PLUGIN_VERSION = 2927b18638429249f80f320c56493d43899009f1
PYTHON_OVOS_OCP_NEWS_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-ocp-news-plugin,$(PYTHON_OVOS_OCP_NEWS_PLUGIN_VERSION))
PYTHON_OVOS_OCP_NEWS_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_OCP_NEWS_PLUGIN_LICENSE_FILE = LICENSE
PYTHON_OVOS_OCP_NEWS_PLUGIN_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
