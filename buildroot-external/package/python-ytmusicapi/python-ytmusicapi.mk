################################################################################
#
# python-ytmusicapi
#
################################################################################

PYTHON_YTMUSICAPI_VERSION = 0.19.4
PYTHON_YTMUSICAPI_SOURCE = ytmusicapi-$(PYTHON_YTMUSICAPI_VERSION).tar.gz
PYTHON_YTMUSICAPI_SITE = https://files.pythonhosted.org/packages/10/f2/d562a14119904808edb1d328e8200fc80f152620267e7a564b468583a626
PYTHON_YTMUSICAPI_SETUP_TYPE = setuptools
PYTHON_YTMUSICAPI_LICENSE = MIT
PYTHON_YTMUSICAPI_LICENSE_FILES = LICENSE

$(eval $(python-package))
