################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = 3eee84f05355918f674260f97fb6bd6494cdfcc3
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
