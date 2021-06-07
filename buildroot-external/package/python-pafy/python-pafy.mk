################################################################################
#
# python-pafy
#
################################################################################

PYTHON_PAFY_VERSION = 0.5.5
PYTHON_PAFY_SOURCE = pafy-$(PYTHON_PAFY_VERSION).tar.gz
PYTHON_PAFY_SITE = https://files.pythonhosted.org/packages/7e/02/b70f4d2ad64bbc7d2a00018c6545d9b9039208553358534e73e6dd5bbaf6
PYTHON_PAFY_SETUP_TYPE = setuptools
PYTHON_PAFY_LICENSE = Public Domain
PYTHON_PAFY_LICENSE_FILES = LICENSE
PYTHON_PAFY_DEPENDENCIES = python-youtube-dl

$(eval $(python-package))
