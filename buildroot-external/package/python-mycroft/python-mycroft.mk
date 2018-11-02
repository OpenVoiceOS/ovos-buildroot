################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = v18.8.4
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,release/$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = 

$(eval $(python-package))
