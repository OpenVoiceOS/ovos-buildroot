################################################################################
#
# python-adafruit-platformdetect
#
################################################################################

PYTHON_ADAFRUIT_PLATFORMDETECT_VERSION = 3.60.0
PYTHON_ADAFRUIT_PLATFORMDETECT_SOURCE = Adafruit-PlatformDetect-$(PYTHON_ADAFRUIT_PLATFORMDETECT_VERSION).tar.gz
PYTHON_ADAFRUIT_PLATFORMDETECT_SITE = https://files.pythonhosted.org/packages/e5/e3/71ba7ff4cbcecf40783613c192bd0ec6c69a70053915567a998ce41050bc
PYTHON_ADAFRUIT_PLATFORMDETECT_SETUP_TYPE = setuptools
PYTHON_ADAFRUIT_PLATFORMDETECT_LICENSE = MIT
PYTHON_ADAFRUIT_PLATFORMDETECT_LICENSE_FILES = LICENSE

$(eval $(python-package))
