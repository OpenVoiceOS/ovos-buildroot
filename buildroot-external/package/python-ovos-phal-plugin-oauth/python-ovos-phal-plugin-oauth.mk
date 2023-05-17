################################################################################
#
# python-ovos-phal-plugin-oauth
#
################################################################################

PYTHON_OVOS_PHAL_PLUGIN_OAUTH_VERSION = 5cdc431cf1d4001a0c02176708d014fa627cbc04
PYTHON_OVOS_PHAL_PLUGIN_OAUTH_SITE = $(call github,OpenVoiceOS,ovos-PHAL-plugin-oauth,$(PYTHON_OVOS_PHAL_PLUGIN_OAUTH_VERSION))
PYTHON_OVOS_PHAL_PLUGIN_OAUTH_SETUP_TYPE = setuptools
PYTHON_OVOS_PHAL_PLUGIN_OAUTH_LICENSE_FILES = LICENSE
PYTHON_OVOS_PHAL_PLUGIN_OAUTH_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
