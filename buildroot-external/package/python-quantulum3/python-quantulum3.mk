################################################################################
#
# python-quantulum3
#
################################################################################

PYTHON_QUANTULUM3_VERSION = 0.7.6
PYTHON_QUANTULUM3_SOURCE = quantulum3-$(PYTHON_QUANTULUM3_VERSION).tar.gz
PYTHON_QUANTULUM3_SITE = https://files.pythonhosted.org/packages/63/ef/95ac4434e8408416e18afc1a76a1c7f8ce55c95ea099851ec0bdf87adca6
PYTHON_QUANTULUM3_SETUP_TYPE = setuptools
PYTHON_QUANTULUM3_LICENSE = MIT

$(eval $(python-package))
