################################################################################
#
# python-adafruit-platformdetect
#
################################################################################

PYTHON_ADAFRUIT_PLATFORMDETECT_VERSION = 3.32.0
PYTHON_ADAFRUIT_PLATFORMDETECT_SOURCE = Adafruit-PlatformDetect-$(PYTHON_ADAFRUIT_PLATFORMDETECT_VERSION).tar.gz
PYTHON_ADAFRUIT_PLATFORMDETECT_SITE = https://files.pythonhosted.org/packages/15/42/2192f64a9732878ddb39bb4359864d1398849e90f39f5591a23005e65d8e
PYTHON_ADAFRUIT_PLATFORMDETECT_SETUP_TYPE = setuptools
PYTHON_ADAFRUIT_PLATFORMDETECT_LICENSE = MIT
PYTHON_ADAFRUIT_PLATFORMDETECT_LICENSE_FILES = LICENSE

$(eval $(python-package))
