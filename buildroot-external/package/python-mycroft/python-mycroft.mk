################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = 599fc576905b2dfc22bfdecbf9f478cc68ebd480
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
