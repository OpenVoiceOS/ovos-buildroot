################################################################################
#
# python-mycroft-messagebus-client
#
################################################################################

PYTHON_MYCROFT_MESSAGEBUS_CLIENT_VERSION = 0.9.1
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_SOURCE = mycroft-messagebus-client-$(PYTHON_MYCROFT_MESSAGEBUS_CLIENT_VERSION).tar.gz
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_SITE = https://files.pythonhosted.org/packages/cf/6f/1ba7f9db76509e650b9e1b4042318d8e662e7b12e3f6e1a3725339f152f8
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_LICENSE = Apache-2.0
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_LICENSE_FILES = LICENSE

$(eval $(python-package))
