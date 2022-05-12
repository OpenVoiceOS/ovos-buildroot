################################################################################
#
# python-mycroft-messagebus-client
#
################################################################################

PYTHON_MYCROFT_MESSAGEBUS_CLIENT_VERSION = 0.9.6
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_SOURCE = mycroft-messagebus-client-$(PYTHON_MYCROFT_MESSAGEBUS_CLIENT_VERSION).tar.gz
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_SITE = https://files.pythonhosted.org/packages/66/d5/32d3db4095b63f9284ed4689c3dbdfa43c5ae02e6895167b3e34161941f5
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_LICENSE = Apache-2.0
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_LICENSE_FILES = LICENSE

$(eval $(python-package))
