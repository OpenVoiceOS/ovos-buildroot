################################################################################
#
# python-gtts
#
################################################################################

PYTHON_GTTS_VERSION = 1.1.7
PYTHON_GTTS_SOURCE = gTTS-$(PYTHON_GTTS_VERSION).tar.gz
PYTHON_GTTS_SITE = https://files.pythonhosted.org/packages/9d/7d/ae1af3b5e4912a630d7aae23c43577799cf49cddd0f5a00a33791d414c2d
PYTHON_GTTS_SETUP_TYPE = setuptools
PYTHON_GTTS_LICENSE = MIT
PYTHON_GTTS_LICENSE_FILES = LICENSE

$(eval $(python-package))
$(eval $(host-python-package))
