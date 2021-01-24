################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = 8020e54eaff9ab064bf56dac6ff3c67da4574a97
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
