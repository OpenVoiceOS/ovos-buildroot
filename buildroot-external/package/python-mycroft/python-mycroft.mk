################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = cafffd8b62c1376e42e13364c4e1e358d7af41e8
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
