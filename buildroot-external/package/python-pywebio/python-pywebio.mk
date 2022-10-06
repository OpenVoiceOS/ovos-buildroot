################################################################################
#
# python-pywebio
#
################################################################################

PYTHON_PYWEBIO_VERSION = 1.6.3
PYTHON_PYWEBIO_SOURCE = pywebio-$(PYTHON_PYWEBIO_VERSION).tar.gz
PYTHON_PYWEBIO_SITE = https://files.pythonhosted.org/packages/d8/46/19f908bbd5563bb2703ceffaafcf488a4dbb2e54a919ed69011e98de5092
PYTHON_PYWEBIO_SETUP_TYPE = setuptools
PYTHON_PYWEBIO_LICENSE = MIT

$(eval $(python-package))
