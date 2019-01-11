################################################################################
#
# python-gtts
#
################################################################################

PYTHON_GTTS_VERSION = 2.0.1
PYTHON_GTTS_SOURCE = gTTS-$(PYTHON_GTTS_VERSION).tar.gz
PYTHON_GTTS_SITE = https://files.pythonhosted.org/packages/52/6e/ae8bd869f7166ab541721e9af7b31d7e54901ce96622620e23e2ae141055
PYTHON_GTTS_SETUP_TYPE = setuptools
PYTHON_GTTS_LICENSE = MIT
PYTHON_GTTS_LICENSE_FILES = LICENSE

$(eval $(python-package))
$(eval $(host-python-package))
