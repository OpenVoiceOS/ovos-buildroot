################################################################################
#
# python-ovos-vlc-plugin
#
################################################################################

PYTHON_OVOS_VLC_PLUGIN_VERSION = 2cdc58b65b4dbe83834f5e23d37066296a17769c
PYTHON_OVOS_VLC_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-vlc-plugin,$(PYTHON_OVOS_VLC_PLUGIN_VERSION))
PYTHON_OVOS_VLC_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_VLC_PLUGIN_LICENSE_FILES = LICENSE

$(eval $(python-package))
