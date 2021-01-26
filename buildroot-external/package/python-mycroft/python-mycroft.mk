################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = 73f0299cfa43f499419d3949fe183cb92da1387e
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
