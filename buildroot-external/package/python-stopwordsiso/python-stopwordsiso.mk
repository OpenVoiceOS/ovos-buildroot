################################################################################
#
# python-stopwordsiso
#
################################################################################

PYTHON_STOPWORDSISO_VERSION = 0.6.1
PYTHON_STOPWORDSISO_SOURCE = stopwordsiso-$(PYTHON_STOPWORDSISO_VERSION).tar.gz
PYTHON_STOPWORDSISO_SITE = https://files.pythonhosted.org/packages/b8/7a/d61b449f4193c6286ae11fead5eb1411e6e7d9362c0ff341bd18442825c4
PYTHON_STOPWORDSISO_SETUP_TYPE = setuptools
PYTHON_STOPWORDSISO_LICENSE = MIT

$(eval $(python-package))
