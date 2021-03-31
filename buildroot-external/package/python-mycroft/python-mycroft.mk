################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = 356288a38fc4f9f71c0dbdb9ddce3b16e702dad2
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
