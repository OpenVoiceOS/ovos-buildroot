################################################################################
#
# python-adafruit-circuitpython-neopixel
#
################################################################################

PYTHON_ADAFRUIT_CIRCUITPYTHON_NEOPIXEL_VERSION = 6.3.6
PYTHON_ADAFRUIT_CIRCUITPYTHON_NEOPIXEL_SOURCE = adafruit-circuitpython-neopixel-$(PYTHON_ADAFRUIT_CIRCUITPYTHON_NEOPIXEL_VERSION).tar.gz
PYTHON_ADAFRUIT_CIRCUITPYTHON_NEOPIXEL_SITE = https://files.pythonhosted.org/packages/07/1a/c4b4ac604b66f7300ff0cb2cfa2d3cead6822e0679b6ffd0c52c17ce082a
PYTHON_ADAFRUIT_CIRCUITPYTHON_NEOPIXEL_SETUP_TYPE = setuptools
PYTHON_ADAFRUIT_CIRCUITPYTHON_NEOPIXEL_LICENSE = MIT
PYTHON_ADAFRUIT_CIRCUITPYTHON_NEOPIXEL_LICENSE_FILES = LICENSE

$(eval $(python-package))
