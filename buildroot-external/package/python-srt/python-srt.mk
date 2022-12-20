################################################################################
#
# python-srt
#
################################################################################

PYTHON_SRT_VERSION = 3.5.2
PYTHON_SRT_SOURCE = srt-$(PYTHON_SRT_VERSION).tar.gz
PYTHON_SRT_SITE = https://files.pythonhosted.org/packages/18/a3/e1466f7c86a9e5d3e462ed6eb3a548917e93cc1ee212cd927f8f4e887ae9
PYTHON_SRT_SETUP_TYPE = setuptools
PYTHON_SRT_LICENSE = MIT
PYTHON_SRT_LICENSE_FILES = LICENSE

$(eval $(python-package))
