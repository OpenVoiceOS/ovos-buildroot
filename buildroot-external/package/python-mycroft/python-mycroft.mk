################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = 1a179dacab94869079755beb83eac735e8d3efe5
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
