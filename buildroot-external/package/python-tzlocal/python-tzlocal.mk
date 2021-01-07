################################################################################
#
# python-tzlocal
#
################################################################################

PYTHON_TZLOCAL_VERSION = 1.3
PYTHON_TZLOCAL_SOURCE = tzlocal-$(PYTHON_TZLOCAL_VERSION).tar.gz
PYTHON_TZLOCAL_SITE = https://files.pythonhosted.org/packages/d3/64/e4b18738496213f82b88b31c431a0e4ece143801fb6771dddd1c2bf0101b
PYTHON_TZLOCAL_SETUP_TYPE = setuptools

$(eval $(python-package))
