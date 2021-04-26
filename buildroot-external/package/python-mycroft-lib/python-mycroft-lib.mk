################################################################################
#
# python-mycroft-lib
#
################################################################################

PYTHON_MYCROFT_LIB_VERSION = ef64e220e78054c51550230510f2b67a54b198c7
PYTHON_MYCROFT_LIB_SITE = $(call github,HelloChatterbox,mycroft-lib,$(PYTHON_MYCROFT_LIB_VERSION))
PYTHON_MYCROFT_LIB_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LIB_LICENSE_FILES = LICENSE

$(eval $(python-package))
