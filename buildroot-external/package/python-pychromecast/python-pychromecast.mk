################################################################################
#
# python-pychromecast
#
################################################################################

PYTHON_PYCHROMECAST_VERSION = 3.2.2
PYTHON_PYCHROMECAST_SOURCE = PyChromecast-$(PYTHON_PYCHROMECAST_VERSION).tar.gz
PYTHON_PYCHROMECAST_SITE = https://files.pythonhosted.org/packages/3d/56/21a75152eb64c16d9379639c408869ae15de553e25af18db3c3bbcfc4bfa
PYTHON_PYCHROMECAST_SETUP_TYPE = setuptools
PYTHON_PYCHROMECAST_LICENSE = MIT
PYTHON_PYCHROMECAST_LICENSE_FILES = LICENSE

$(eval $(python-package))
