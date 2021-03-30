################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = fd4e0dc160391f1b5703c66f9482e93d30c15118
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
