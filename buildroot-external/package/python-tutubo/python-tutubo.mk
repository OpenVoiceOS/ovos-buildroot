################################################################################
#
# python-tutubo
#
################################################################################

PYTHON_TUTUBO_VERSION = 0.0.1a3
PYTHON_TUTUBO_SOURCE = tutubo-$(PYTHON_TUTUBO_VERSION).tar.gz
PYTHON_TUTUBO_SITE = https://files.pythonhosted.org/packages/3b/b3/1d9c5a70b5ab05a256995919b464914a2df33a59c2ad6958701e852206cf
PYTHON_TUTUBO_SETUP_TYPE = setuptools
PYTHON_TUTUBO_LICENSE = Apache

$(eval $(python-package))
