################################################################################
#
# python-pychromecast
#
################################################################################

PYTHON_PYCHROMECAST_VERSION = 0.7.7
PYTHON_PYCHROMECAST_SOURCE = PyChromecast-$(PYTHON_PYCHROMECAST_VERSION).tar.gz
PYTHON_PYCHROMECAST_SITE = https://files.pythonhosted.org/packages/cf/07/9a95c424e080f4b4e3b0b58cc91e67b03ce67e7f1a4f204e886d2838665f
PYTHON_PYCHROMECAST_SETUP_TYPE = setuptools
PYTHON_PYCHROMECAST_LICENSE = MIT
PYTHON_PYCHROMECAST_LICENSE_FILES = LICENSE

$(eval $(python-package))
