################################################################################
#
# python-zipp
#
################################################################################

PYTHON_ZIPP_VERSION = 3.15.0
PYTHON_ZIPP_SOURCE = zipp-$(PYTHON_ZIPP_VERSION).tar.gz
PYTHON_ZIPP_SITE = https://files.pythonhosted.org/packages/00/27/f0ac6b846684cecce1ee93d32450c45ab607f65c2e0255f0092032d91f07
PYTHON_ZIPP_SETUP_TYPE = setuptools

$(eval $(python-package))
