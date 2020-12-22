################################################################################
#
# python-gtts
#
################################################################################

PYTHON_GTTS_VERSION = 2.2.0
PYTHON_GTTS_SOURCE = gTTS-$(PYTHON_GTTS_VERSION).tar.gz
PYTHON_GTTS_SITE = https://files.pythonhosted.org/packages/f8/a2/826a16210ccaba75c48414428bb4ca3cc2fddee5935fc3e49a8af417af92
PYTHON_GTTS_SETUP_TYPE = setuptools
PYTHON_GTTS_LICENSE = MIT
PYTHON_GTTS_LICENSE_FILES = LICENSE

$(eval $(python-package))
