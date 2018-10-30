################################################################################
#
# python-pygithub
#
################################################################################

PYTHON_PYGITHUB_VERSION = 1.43.2
PYTHON_PYGITHUB_SOURCE = PyGithub-$(PYTHON_PYGITHUB_VERSION).tar.gz
PYTHON_PYGITHUB_SITE = https://files.pythonhosted.org/packages/91/9e/50af4bb0ab316fedc13ae87347a718c19698ba8a19e64a692dc30c5fc9db
PYTHON_PYGITHUB_SETUP_TYPE = setuptools
PYTHON_PYGITHUB_LICENSE = 
PYTHON_PYGITHUB_LICENSE_FILES = 

$(eval $(python-package))
