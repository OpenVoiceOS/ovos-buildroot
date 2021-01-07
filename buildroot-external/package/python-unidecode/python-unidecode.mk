################################################################################
#
# python-unidecode
#
################################################################################

PYTHON_UNIDECODE_VERSION = 1.1.2
PYTHON_UNIDECODE_SOURCE = Unidecode-$(PYTHON_UNIDECODE_VERSION).tar.gz
PYTHON_UNIDECODE_SITE = https://files.pythonhosted.org/packages/45/dd/544c34ddf9ab0ead3746110ad6fbdac26ca5f4a1666db22dc8aaf447d0c9
PYTHON_UNIDECODE_SETUP_TYPE = setuptools
PYTHON_UNIDECODE_LICENSE = GPL-2.0
PYTHON_UNIDECODE_LICENSE_FILES = LICENSE

$(eval $(python-package))
