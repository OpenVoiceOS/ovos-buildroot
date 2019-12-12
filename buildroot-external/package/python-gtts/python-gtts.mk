################################################################################
#
# python-gtts
#
################################################################################

PYTHON_GTTS_VERSION = 2.0.4
PYTHON_GTTS_SOURCE = gTTS-$(PYTHON_GTTS_VERSION).tar.gz
PYTHON_GTTS_SITE = https://files.pythonhosted.org/packages/6b/1c/4c4e9ddde4856e9ea44c6f2e5cb9785cca446ce9addd81ffd1cacad6ddec
PYTHON_GTTS_SETUP_TYPE = setuptools
PYTHON_GTTS_LICENSE = MIT
PYTHON_GTTS_LICENSE_FILES = LICENSE

$(eval $(python-package))
