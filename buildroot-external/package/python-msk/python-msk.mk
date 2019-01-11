################################################################################
#
# python-msk
#
################################################################################

PYTHON_MSK_VERSION = 0.3.12
PYTHON_MSK_SOURCE = msk-$(PYTHON_MSK_VERSION).tar.gz
PYTHON_MSK_SITE = https://files.pythonhosted.org/packages/34/91/fad24465ad7d07184d2b7e965415f62acf90e5488cfd3fec56c89430f01b
PYTHON_MSK_SETUP_TYPE = setuptools

$(eval $(python-package))
