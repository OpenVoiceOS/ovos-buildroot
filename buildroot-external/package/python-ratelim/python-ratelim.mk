################################################################################
#
# python-ratelim
#
################################################################################

PYTHON_RATELIM_VERSION = 0.1.6
PYTHON_RATELIM_SOURCE = ratelim-$(PYTHON_RATELIM_VERSION).tar.gz
PYTHON_RATELIM_SITE = https://files.pythonhosted.org/packages/c5/5a/e1440017bccb14523bb76356e6f3a5468386b8a9192bd901e98babd1a1ea
PYTHON_RATELIM_SETUP_TYPE = setuptools

$(eval $(python-package))
