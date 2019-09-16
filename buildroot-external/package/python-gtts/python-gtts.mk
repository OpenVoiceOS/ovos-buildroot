################################################################################
#
# python-gtts
#
################################################################################

PYTHON_GTTS_VERSION = 2.0.3
PYTHON_GTTS_SOURCE = gTTS-$(PYTHON_GTTS_VERSION).tar.gz
PYTHON_GTTS_SITE = https://files.pythonhosted.org/packages/e6/37/f55346a736278f0eb0ae9f7edee1a61028735ef0010db68a2e6fcd0ece56
PYTHON_GTTS_SETUP_TYPE = setuptools
PYTHON_GTTS_LICENSE = MIT
PYTHON_GTTS_LICENSE_FILES = LICENSE

$(eval $(python-package))
$(eval $(host-python-package))
