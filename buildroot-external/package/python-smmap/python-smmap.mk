################################################################################
#
# python-smmap
#
################################################################################

PYTHON_SMMAP_VERSION = 3.0.4
PYTHON_SMMAP_SOURCE = smmap-$(PYTHON_SMMAP_VERSION).tar.gz
PYTHON_SMMAP_SITE = https://files.pythonhosted.org/packages/75/fb/2f594e5364f9c986b2c89eb662fc6067292cb3df2b88ae31c939b9138bb9
PYTHON_SMMAP_SETUP_TYPE = setuptools
PYTHON_SMMAP_LICENSE = BSD-3-Clause
PYTHON_SMMAP_LICENSE_FILES = LICENSE

$(eval $(python-package))
