################################################################################
#
# python-rakekeywords
#
################################################################################

PYTHON_RAKEKEYWORDS_VERSION = 0.2.0
PYTHON_RAKEKEYWORDS_SOURCE = RAKEkeywords-$(PYTHON_RAKEKEYWORDS_VERSION).tar.gz
PYTHON_RAKEKEYWORDS_SITE = https://files.pythonhosted.org/packages/fc/7f/325d2d5660e4022a50b268aa6592954332e6607398922bd7c0210de259be
PYTHON_RAKEKEYWORDS_SETUP_TYPE = setuptools
PYTHON_RAKEKEYWORDS_LICENSE = Apache2

$(eval $(python-package))
