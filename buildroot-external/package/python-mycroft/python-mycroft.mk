################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = 7f7c97d0f6e6dc02a3b4af95887294e80092a2eb
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
