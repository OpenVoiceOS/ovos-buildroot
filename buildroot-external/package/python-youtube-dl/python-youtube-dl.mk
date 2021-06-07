################################################################################
#
# python-youtube-dl
#
################################################################################

PYTHON_YOUTUBE_DL_VERSION = 2021.6.6
PYTHON_YOUTUBE_DL_SOURCE = youtube_dl-$(PYTHON_YOUTUBE_DL_VERSION).tar.gz
PYTHON_YOUTUBE_DL_SITE = https://files.pythonhosted.org/packages/c6/75/05979677d9abc76851d13d8db3951e39017ac223545adab6e8576fa0cbe7
PYTHON_YOUTUBE_DL_SETUP_TYPE = setuptools
PYTHON_YOUTUBE_DL_LICENSE = Public Domain
PYTHON_YOUTUBE_DL_LICENSE_FILES = LICENSE
PYTHON_YOUTUBE_DL_INSTALL_STAGING = YES

$(eval $(python-package))
