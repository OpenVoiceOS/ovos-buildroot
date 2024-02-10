################################################################################
#
# python-adafruit-blinka
#
################################################################################

PYTHON_ADAFRUIT_BLINKA_VERSION = 8.31.0
PYTHON_ADAFRUIT_BLINKA_SOURCE = Adafruit-Blinka-$(PYTHON_ADAFRUIT_BLINKA_VERSION).tar.gz
PYTHON_ADAFRUIT_BLINKA_SITE = https://files.pythonhosted.org/packages/74/ed/e51689be726338ba16f2a88373ad4690702c5ddf8668be1b0289cb279840
PYTHON_ADAFRUIT_BLINKA_SETUP_TYPE = setuptools
PYTHON_ADAFRUIT_BLINKA_LICENSE = MIT
PYTHON_ADAFRUIT_BLINKA_LICENSE_FILES = LICENSE
PYTHON_ADAFRUIT_BLINKA_BIN_ARCH_EXCLUDE = usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/adafruit_blinka/microcontroller/bcm283x/pulseio
PYTHON_ADAFRUIT_BLINKA_BIN_ARCH_EXCLUDE += usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/adafruit_blinka/microcontroller/amlogic/a311d/pulseio

$(eval $(python-package))
