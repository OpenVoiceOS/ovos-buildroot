################################################################################
#
# python-mycroft-lib
#
################################################################################

PYTHON_MYCROFT_LIB_VERSION = ab6ac7713ecc2bf4eb0430ea05dfcf06bbc5dd3a
PYTHON_MYCROFT_LIB_SITE = $(call github,HelloChatterbox,mycroft-lib,$(PYTHON_MYCROFT_LIB_VERSION))
PYTHON_MYCROFT_LIB_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LIB_LICENSE_FILES = LICENSE

$(eval $(python-package))
