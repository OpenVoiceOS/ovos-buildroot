################################################################################
#
# python-tflit
#
################################################################################

PYTHON_TFLIT_VERSION = 0.1.2
PYTHON_TFLIT_SOURCE = tflit-$(PYTHON_TFLIT_VERSION).tar.gz
PYTHON_TFLIT_SITE = https://files.pythonhosted.org/packages/34/e2/cda67aa652074f760c9aa3e17929224a9b3c42187256c8cf366908ce3c34
PYTHON_TFLIT_SETUP_TYPE = setuptools

$(eval $(python-package))
