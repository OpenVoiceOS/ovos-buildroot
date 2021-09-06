################################################################################
#
# python-mycroft-messagebus-client
#
################################################################################

PYTHON_MYCROFT_MESSAGEBUS_CLIENT_VERSION = 6333d715662c5ebdcabe38375f81acbbe888d821
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_SITE = $(call github,OpenVoiceOS,mycroft-messagebus-client,$(PYTHON_MYCROFT_MESSAGEBUS_CLIENT_VERSION))
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_LICENSE = Apache-2.0
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_LICENSE_FILES = LICENSE

$(eval $(python-package))
