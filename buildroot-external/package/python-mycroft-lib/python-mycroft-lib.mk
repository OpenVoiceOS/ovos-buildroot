################################################################################
#
# python-mycroft-lib
#
################################################################################

PYTHON_MYCROFT_LIB_VERSION = 496a0fcc9d1dd22cc13f252835ade1a5f3c7c879
PYTHON_MYCROFT_LIB_SITE = $(call github,HelloChatterbox,mycroft-lib,$(PYTHON_MYCROFT_LIB_VERSION))
PYTHON_MYCROFT_LIB_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LIB_LICENSE_FILES = LICENSE

$(eval $(python-package))
