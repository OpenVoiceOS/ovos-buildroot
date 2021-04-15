################################################################################
#
# python-mycroft-lib
#
################################################################################

PYTHON_MYCROFT_LIB_VERSION = 3110929346a9d0d9adb091f9f8f0c7d093ba2920
PYTHON_MYCROFT_LIB_SITE = $(call github,HelloChatterbox,mycroft-lib,$(PYTHON_MYCROFT_LIB_VERSION))
PYTHON_MYCROFT_LIB_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LIB_LICENSE_FILES = LICENSE

$(eval $(python-package))
