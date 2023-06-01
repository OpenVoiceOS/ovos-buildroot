################################################################################
#
# python-timezonefinder
#
################################################################################

PYTHON_TIMEZONEFINDER_VERSION = 6.2.0
PYTHON_TIMEZONEFINDER_SOURCE = timezonefinder-$(PYTHON_TIMEZONEFINDER_VERSION).tar.gz
PYTHON_TIMEZONEFINDER_SITE = https://files.pythonhosted.org/packages/e7/68/86c8d0b21573150eb7b3c66da2c451159b0159c15d3d59b17777ea557f48
PYTHON_TIMEZONEFINDER_SETUP_TYPE = pep517 #flit #setuptools
PYTHON_TIMEZONEFINDER_DEPENDENCIES = host-python-numpy

$(eval $(python-package))
