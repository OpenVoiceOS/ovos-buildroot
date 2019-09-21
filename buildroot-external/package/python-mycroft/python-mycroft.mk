################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = 6c228d00a914d3d1ba0506cd216089f21706eb43
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
