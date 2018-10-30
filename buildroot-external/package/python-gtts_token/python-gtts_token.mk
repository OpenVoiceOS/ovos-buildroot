################################################################################
#
# python-gtts_token
#
################################################################################

PYTHON_GTTS_TOKEN_VERSION = 1.1.2
PYTHON_GTTS_TOKEN_SOURCE = gTTS-token-$(PYTHON_GTTS_TOKEN_VERSION).tar.gz
PYTHON_GTTS_TOKEN_SITE = https://files.pythonhosted.org/packages/5a/81/b54c771ee6a78bdb6aebc274d7a806ad1f8761462f3592f3781d5cd9046f
PYTHON_GTTS_TOKEN_SETUP_TYPE = setuptools
PYTHON_GTTS_TOKEN_LICENSE = MIT

$(eval $(python-package))
