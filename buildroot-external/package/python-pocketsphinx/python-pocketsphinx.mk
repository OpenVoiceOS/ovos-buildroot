################################################################################
#
# python-pocketsphinx
#
################################################################################

PYTHON_POCKETSPHINX_VERSION = 0.1.15
PYTHON_POCKETSPHINX_SOURCE = pocketsphinx-$(PYTHON_POCKETSPHINX_VERSION).tar.gz
PYTHON_POCKETSPHINX_SITE = https://files.pythonhosted.org/packages/cd/4a/adea55f189a81aed88efa0b0e1d25628e5ed22622ab9174bf696dd4f9474
PYTHON_POCKETSPHINX_SETUP_TYPE = setuptools
PYTHON_POCKETSPHINX_LICENSE_FILES = LICENSE

$(eval $(python-package))
