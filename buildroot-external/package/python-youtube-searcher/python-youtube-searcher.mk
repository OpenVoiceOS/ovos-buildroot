################################################################################
#
# python-youtube-searcher
#
################################################################################

PYTHON_YOUTUBE_SEARCHER_VERSION = 0.1.6
PYTHON_YOUTUBE_SEARCHER_SOURCE = youtube_searcher-$(PYTHON_YOUTUBE_SEARCHER_VERSION).tar.gz
PYTHON_YOUTUBE_SEARCHER_SITE = https://files.pythonhosted.org/packages/e9/7c/c95ce24b6f36d51cc5c41b79265ca5181157a455d95a7c958bc082cfe8c4
PYTHON_YOUTUBE_SEARCHER_SETUP_TYPE = setuptools
PYTHON_YOUTUBE_SEARCHER_LICENSE = Apache

$(eval $(python-package))
