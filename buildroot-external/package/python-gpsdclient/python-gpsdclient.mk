################################################################################
#
# python-gpsdclient
#
################################################################################

PYTHON_GPSDCLIENT_VERSION = 1.2.1
PYTHON_GPSDCLIENT_SOURCE = gpsdclient-$(PYTHON_GPSDCLIENT_VERSION).tar.gz
PYTHON_GPSDCLIENT_SITE = https://files.pythonhosted.org/packages/fa/c7/b1e616a6e75f0ff8dfd193a9f517776a132ef1ae15e309775bbd223f759d
PYTHON_GPSDCLIENT_SETUP_TYPE = setuptools
PYTHON_GPSDCLIENT_LICENSE = MIT
PYTHON_GPSDCLIENT_LICENSE_FILES = LICENSE.txt

$(eval $(python-package))
