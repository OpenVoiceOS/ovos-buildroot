################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = 8a3cf544cd26e1e5ff6ea46b55fc093fc04ab246
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
