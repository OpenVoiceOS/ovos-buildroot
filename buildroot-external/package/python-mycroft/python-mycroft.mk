################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = e69f3517c8323df0afb6df447821c9dcca343e27
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
