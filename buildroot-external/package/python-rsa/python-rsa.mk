################################################################################
#
# python-rsa
#
################################################################################

PYTHON_RSA_VERSION = 4.0
PYTHON_RSA_SOURCE = rsa-$(PYTHON_RSA_VERSION).tar.gz
PYTHON_RSA_SITE = https://files.pythonhosted.org/packages/cb/d0/8f99b91432a60ca4b1cd478fd0bdf28c1901c58e3a9f14f4ba3dba86b57f
PYTHON_RSA_SETUP_TYPE = setuptools
PYTHON_RSA_LICENSE = 
PYTHON_RSA_LICENSE_FILES = 

$(eval $(python-package))
