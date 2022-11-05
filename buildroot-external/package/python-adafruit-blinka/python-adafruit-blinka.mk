################################################################################
#
# python-adafruit-blinka
#
################################################################################

PYTHON_ADAFRUIT_BLINKA_VERSION = 8.6.0
PYTHON_ADAFRUIT_BLINKA_SOURCE = Adafruit-Blinka-$(PYTHON_ADAFRUIT_BLINKA_VERSION).tar.gz
PYTHON_ADAFRUIT_BLINKA_SITE = https://files.pythonhosted.org/packages/76/29/541a6a22d923fbe0d4cf52f953a2c737370cb717f8df1cbd95ab97fe2fba
PYTHON_ADAFRUIT_BLINKA_SETUP_TYPE = setuptools
PYTHON_ADAFRUIT_BLINKA_LICENSE = MIT
PYTHON_ADAFRUIT_BLINKA_LICENSE_FILES = LICENSE

$(eval $(python-package))
