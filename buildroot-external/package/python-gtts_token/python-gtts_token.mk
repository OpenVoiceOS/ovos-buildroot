################################################################################
#
# python-gtts_token
#
################################################################################

PYTHON_GTTS_TOKEN_VERSION = 1.1.3
PYTHON_GTTS_TOKEN_SOURCE = gTTS-token-$(PYTHON_GTTS_TOKEN_VERSION).tar.gz
PYTHON_GTTS_TOKEN_SITE = https://files.pythonhosted.org/packages/e7/25/ca6e9cd3275bfc3097fe6b06cc31db6d3dfaf32e032e0f73fead9c9a03ce
PYTHON_GTTS_TOKEN_SETUP_TYPE = setuptools
PYTHON_GTTS_TOKEN_LICENSE = MIT

$(eval $(python-package))
