################################################################################
#
# python-timezonefinder
#
################################################################################

PYTHON_TIMEZONEFINDER_VERSION = 5.0.0
PYTHON_TIMEZONEFINDER_SOURCE = timezonefinder-$(PYTHON_TIMEZONEFINDER_VERSION).tar.gz
PYTHON_TIMEZONEFINDER_SITE = https://files.pythonhosted.org/packages/74/d2/e6cc8edf6a6da56c5311776334b4bd2a271757573dd020592a8540512b88
PYTHON_TIMEZONEFINDER_SETUP_TYPE = setuptools
PYTHON_TIMEZONEFINDER_DEPENDENCIES = host-python-numpy

$(eval $(python-package))
