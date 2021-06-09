################################################################################
#
# python-url-normalize
#
################################################################################

PYTHON_URL_NORMALIZE_VERSION = 1.4.3
PYTHON_URL_NORMALIZE_SOURCE = url-normalize-$(PYTHON_URL_NORMALIZE_VERSION).tar.gz
PYTHON_URL_NORMALIZE_SITE = https://files.pythonhosted.org/packages/ec/ea/780a38c99fef750897158c0afb83b979def3b379aaac28b31538d24c4e8f
PYTHON_URL_NORMALIZE_SETUP_TYPE = setuptools
PYTHON_URL_NORMALIZE_LICENSE = MIT
PYTHON_URL_NORMALIZE_LICENSE_FILES = LICENSE

$(eval $(python-package))
