################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = bfd6be347f0c88aabad8f287081a860b09359f3d
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
