################################################################################
#
# python-requests-futures
#
################################################################################

PYTHON_REQUESTS_FUTURES_VERSION = 0.9.5
PYTHON_REQUESTS_FUTURES_SOURCE = requests-futures-$(PYTHON_REQUESTS_FUTURES_VERSION).tar.gz
PYTHON_REQUESTS_FUTURES_SITE = https://files.pythonhosted.org/packages/25/43/bf8e46a309b5bb08f9d7813473ddb5f27a40d194ddf120fa4f193aa764e3
PYTHON_REQUESTS_FUTURES_SETUP_TYPE = setuptools
PYTHON_REQUESTS_FUTURES_LICENSE = Apache License v2
PYTHON_REQUESTS_FUTURES_LICENSE_FILES = LICENSE

$(eval $(python-package))
$(eval $(host-python-package))
