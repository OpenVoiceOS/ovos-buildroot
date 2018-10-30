################################################################################
#
# python-pocketsphinx
#
################################################################################

PYTHON_POCKETSPHINX_VERSION = 0.1.0
PYTHON_POCKETSPHINX_SOURCE = pocketsphinx-$(PYTHON_POCKETSPHINX_VERSION).tar.gz
PYTHON_POCKETSPHINX_SITE = https://files.pythonhosted.org/packages/25/73/1d4f4734e2afe72bec6756853e7cdcffbb05115045fcea471224537243bd
PYTHON_POCKETSPHINX_SETUP_TYPE = setuptools
PYTHON_POCKETSPHINX_LICENSE_FILES = LICENSE

$(eval $(python-package))
