################################################################################
#
# python-hijri-converter
#
################################################################################

PYTHON_HIJRI_CONVERTER_VERSION = 2.2.4
PYTHON_HIJRI_CONVERTER_SOURCE = hijri-converter-$(PYTHON_HIJRI_CONVERTER_VERSION).tar.gz
PYTHON_HIJRI_CONVERTER_SITE = https://files.pythonhosted.org/packages/54/6f/96f9880389a20057ce3fdfed70a9cea5eb47d679178a43c55f58a35d98be
PYTHON_HIJRI_CONVERTER_SETUP_TYPE = setuptools
PYTHON_HIJRI_CONVERTER_LICENSE = MIT
PYTHON_HIJRI_CONVERTER_LICENSE_FILES = LICENSE

$(eval $(python-package))
