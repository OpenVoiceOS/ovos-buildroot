################################################################################
#
# python-yt-dlp
#
################################################################################

PYTHON_YT_DLP_VERSION = 2021.12.27
PYTHON_YT_DLP_SOURCE = yt-dlp-$(PYTHON_YT_DLP_VERSION).tar.gz
PYTHON_YT_DLP_SITE = https://files.pythonhosted.org/packages/e0/c5/1748e553776f00057fb4b0f648eb22b7e0d58a3c062d2d4a6b8aba72fb4e
PYTHON_YT_DLP_SETUP_TYPE = setuptools
PYTHON_YT_DLP_LICENSE = Public Domain
PYTHON_YT_DLP_LICENSE_FILES = LICENSE

$(eval $(python-package))
