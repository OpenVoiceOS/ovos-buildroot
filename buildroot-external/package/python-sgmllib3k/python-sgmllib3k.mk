################################################################################
#
# python-sgmllib3k
#
################################################################################

PYTHON_SGMLLIB3K_VERSION = 1.0.0
PYTHON_SGMLLIB3K_SOURCE = sgmllib3k-$(PYTHON_SGMLLIB3K_VERSION).tar.gz
PYTHON_SGMLLIB3K_SITE = https://files.pythonhosted.org/packages/9e/bd/3704a8c3e0942d711c1299ebf7b9091930adae6675d7c8f476a7ce48653c
PYTHON_SGMLLIB3K_SETUP_TYPE = setuptools

$(eval $(python-package))
