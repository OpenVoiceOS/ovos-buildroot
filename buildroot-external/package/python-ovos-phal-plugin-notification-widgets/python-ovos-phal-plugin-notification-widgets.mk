################################################################################
#
# python-ovos-phal-plugin-notification-widgets
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_VERSION = 6369bbed41559d3030e3aa93938790b855282451
PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-notification-widgets,$(PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_LICENSE_FILES = LICENSE

$(eval $(python-package))
