################################################################################
#
# python-gtts
#
################################################################################

PYTHON_GTTS_VERSION = 2.2.2
PYTHON_GTTS_SOURCE = gTTS-$(PYTHON_GTTS_VERSION).tar.gz
PYTHON_GTTS_SITE = https://files.pythonhosted.org/packages/ec/fa/cc7d5d6669f893b976be10fe9fb2cce2be0947db9916eb3fbdabcd4a2a31
PYTHON_GTTS_SETUP_TYPE = setuptools
PYTHON_GTTS_LICENSE = MIT
PYTHON_GTTS_LICENSE_FILES = LICENSE

$(eval $(python-package))
