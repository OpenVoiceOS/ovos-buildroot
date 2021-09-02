################################################################################
#
# python-premailer
#
################################################################################

PYTHON_PREMAILER_VERSION = 3.10.0
PYTHON_PREMAILER_SOURCE = premailer-$(PYTHON_PREMAILER_VERSION).tar.gz
PYTHON_PREMAILER_SITE = https://files.pythonhosted.org/packages/a3/6f/e49bd31941eff2987076383fa6d811eb785a28f498f5bb131e981bd71e13
PYTHON_PREMAILER_SETUP_TYPE = setuptools
PYTHON_PREMAILER_LICENSE = Python Software Foundation License
PYTHON_PREMAILER_LICENSE_FILES = LICENSE

$(eval $(python-package))
