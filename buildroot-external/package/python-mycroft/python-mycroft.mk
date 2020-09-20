################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = 2e1247dd5c5fc1c767b40acb32535da2502e050b
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
