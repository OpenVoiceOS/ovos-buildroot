################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = 0050bde937e1741356031d2adca1fbc0cfcb3fb7
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
