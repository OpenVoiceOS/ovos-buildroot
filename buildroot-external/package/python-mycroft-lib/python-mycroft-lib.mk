################################################################################
#
# python-mycroft-lib
#
################################################################################

PYTHON_MYCROFT_LIB_VERSION = de69f365d513311eb1be18f6d149feaca67a18d3
PYTHON_MYCROFT_LIB_SITE = $(call github,HelloChatterbox,mycroft-lib,$(PYTHON_MYCROFT_LIB_VERSION))
PYTHON_MYCROFT_LIB_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LIB_LICENSE_FILES = LICENSE

$(eval $(python-package))
