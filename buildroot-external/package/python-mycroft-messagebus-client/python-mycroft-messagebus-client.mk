################################################################################
#
# python-mycroft-messagebus-client
#
################################################################################

PYTHON_MYCROFT_MESSAGEBUS_CLIENT_VERSION = 0951b249b98d9a8ceba7b78c9e3ebc4e64aa36d0
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_SITE = $(call github,OpenVoiceOS,mycroft-messagebus-client,$(PYTHON_MYCROFT_MESSAGEBUS_CLIENT_VERSION))
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_LICENSE = Apache-2.0
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_LICENSE_FILES = LICENSE

$(eval $(python-package))
