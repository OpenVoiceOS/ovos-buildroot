################################################################################
#
# python-geocoder
#
################################################################################

PYTHON_GEOCODER_VERSION = 1.38.1
PYTHON_GEOCODER_SOURCE = geocoder-$(PYTHON_GEOCODER_VERSION).tar.gz
PYTHON_GEOCODER_SITE = https://files.pythonhosted.org/packages/ea/0b/2ea440270c1efb7ac73450cb704344c8127f45dabff0bea48711dc9dd93a
PYTHON_GEOCODER_SETUP_TYPE = setuptools
PYTHON_GEOCODER_LICENSE = MIT
PYTHON_GEOCODER_LICENSE_FILES = LICENSE

$(eval $(python-package))
