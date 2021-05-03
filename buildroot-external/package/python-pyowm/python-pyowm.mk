################################################################################
#
# python-pyowm
#
################################################################################

PYTHON_PYOWM_VERSION = 2.6.1
PYTHON_PYOWM_SOURCE = pyowm-$(PYTHON_PYOWM_VERSION).tar.gz
PYTHON_PYOWM_SITE = https://files.pythonhosted.org/packages/3a/1b/94282ac9ea7f737a6eea9520fed026200b63853b3196392814506c456b00
PYTHON_PYOWM_SETUP_TYPE = distutils
PYTHON_PYOWM_LICENSE = MIT

$(eval $(python-package))
