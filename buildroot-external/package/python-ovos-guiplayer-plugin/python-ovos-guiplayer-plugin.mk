################################################################################
#
# python-ovos-guiplayer-plugin
#
################################################################################

PYTHON_OVOS_GUIPLAYER_PLUGIN_VERSION = 01ab75f869820f9737b0791b59e63819e61729b9
PYTHON_OVOS_GUIPLAYER_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-guiplayer-plugin,$(PYTHON_OVOS_GUIPLAYER_PLUGIN_VERSION))
PYTHON_OVOS_GUIPLAYER_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_GUIPLAYER_PLUGIN_LICENSE_FILES = LICENSE

$(eval $(python-package))
