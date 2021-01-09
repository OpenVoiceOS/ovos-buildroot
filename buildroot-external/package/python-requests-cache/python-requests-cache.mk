################################################################################
#
# python-requests-cache
#
################################################################################

PYTHON_REQUESTS_CACHE_VERSION = 0.5.2
PYTHON_REQUESTS_CACHE_SOURCE = requests-cache-$(PYTHON_REQUESTS_CACHE_VERSION).tar.gz
PYTHON_REQUESTS_CACHE_SITE = https://files.pythonhosted.org/packages/0c/d4/bdc22aad6979ceeea2638297f213108aeb5e25c7b103fa02e4acbe43992e
PYTHON_REQUESTS_CACHE_SETUP_TYPE = setuptools
PYTHON_REQUESTS_CACHE_LICENSE = BSD-2-Clause
PYTHON_REQUESTS_CACHE_LICENSE_FILES = LICENSE

$(eval $(python-package))
