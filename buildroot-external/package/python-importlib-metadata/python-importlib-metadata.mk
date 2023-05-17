################################################################################
#
# python-importlib-metadata
#
################################################################################

PYTHON_IMPORTLIB_METADATA_VERSION = 6.6.0
PYTHON_IMPORTLIB_METADATA_SOURCE = importlib_metadata-$(PYTHON_IMPORTLIB_METADATA_VERSION).tar.gz
PYTHON_IMPORTLIB_METADATA_SITE = https://files.pythonhosted.org/packages/0b/1f/9de392c2b939384e08812ef93adf37684ec170b5b6e7ea302d9f163c2ea0
PYTHON_IMPORTLIB_METADATA_SETUP_TYPE = setuptools

$(eval $(python-package))
