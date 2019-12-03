################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = 21699294c782edfd9919999ecbf0f5de441330e4
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
