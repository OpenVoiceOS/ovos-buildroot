################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = fc7847029c368bfc4d674f2255aa01d0e6fb0cf0
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
