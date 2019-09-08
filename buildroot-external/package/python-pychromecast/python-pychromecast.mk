################################################################################
#
# python-pychromecast
#
################################################################################

PYTHON_PYCHROMECAST_VERSION = 3.2.3
PYTHON_PYCHROMECAST_SOURCE = PyChromecast-$(PYTHON_PYCHROMECAST_VERSION).tar.gz
PYTHON_PYCHROMECAST_SITE = https://files.pythonhosted.org/packages/ec/94/c5fa90465f9a4f8266d4feefc3f39f3a5caa1f342825f298c638cc582ebf
PYTHON_PYCHROMECAST_SETUP_TYPE = setuptools
PYTHON_PYCHROMECAST_LICENSE = MIT
PYTHON_PYCHROMECAST_LICENSE_FILES = LICENSE

$(eval $(python-package))
