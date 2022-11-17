################################################################################
#
# python-ovos-phal-plugin-notification-widgets
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_VERSION = 9991c58463d3449c541adfbfc2e1ec12de76fa08
PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-notification-widgets,$(PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_NOTIFICATION_WIDGETS_LICENSE_FILES = LICENSE

$(eval $(python-package))
