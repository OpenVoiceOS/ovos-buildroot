################################################################################
#
# python-ovos-vlc-plugin
#
################################################################################

PYTHON_OVOS_VLC_PLUGIN_VERSION = 7f7d778d08bc64e17f660680b36aae0d353f01e6
PYTHON_OVOS_VLC_PLUGIN_SITE = $(call github,OpenVoiceOS,ovos-vlc-plugin,$(PYTHON_OVOS_VLC_PLUGIN_VERSION))
PYTHON_OVOS_VLC_PLUGIN_SETUP_TYPE = setuptools
PYTHON_OVOS_VLC_PLUGIN_LICENSE_FILES = LICENSE

$(eval $(python-package))
