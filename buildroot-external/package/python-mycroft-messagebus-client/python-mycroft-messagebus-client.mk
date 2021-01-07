################################################################################
#
# python-mycroft-messagebus-client
#
################################################################################

PYTHON_MYCROFT_MESSAGEBUS_CLIENT_VERSION = 0.8.4
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_SOURCE = mycroft-messagebus-client-$(PYTHON_MYCROFT_MESSAGEBUS_CLIENT_VERSION).tar.gz
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_SITE = https://files.pythonhosted.org/packages/06/15/881da04555710caa2b5fd0d582aa21ed6ecaf88fc5c2343f46caa1b84ccf
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_LICENSE = Apache-2.0
PYTHON_MYCROFT_MESSAGEBUS_CLIENT_LICENSE_FILES = LICENSE

$(eval $(python-package))
