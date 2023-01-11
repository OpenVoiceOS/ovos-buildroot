################################################################################
#
# python-ovos-ocp-youtube-plugin
#
################################################################################

PYTHON_OVOS_OCP_YOUTUBE_PLUGIN_VERSION = eb77b2c753e0afaf4d76172d40272222f05229eb
PYTHON_OVOS_OCP_YOUTUBE_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-ocp-youtube-plugin,$(PYTHON_OVOS_OCP_YOUTUBE_PLUGIN_VERSION))
PYTHON_OVOS_OCP_YOUTUBE_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_OCP_YOUTUBE_PLUGIN_LICENSE_YOUTUBE = LICENSE
PYTHON_OVOS_OCP_YOUTUBE_PLUGIN_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
