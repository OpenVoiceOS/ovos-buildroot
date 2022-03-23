################################################################################
#
# python-reverse-geocoder
#
################################################################################

PYTHON_REVERSE_GEOCODER_VERSION = 1.5.1
PYTHON_REVERSE_GEOCODER_SOURCE = reverse_geocoder-$(PYTHON_REVERSE_GEOCODER_VERSION).tar.gz
PYTHON_REVERSE_GEOCODER_SITE = https://files.pythonhosted.org/packages/0b/0f/b7d5d4b36553731f11983e19e1813a1059ad0732c5162c01b3220c927d31
PYTHON_REVERSE_GEOCODER_SETUP_TYPE = setuptools
PYTHON_REVERSE_GEOCODER_LICENSE = lgpl

$(eval $(python-package))
