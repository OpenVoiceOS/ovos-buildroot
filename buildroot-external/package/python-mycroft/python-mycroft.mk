################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = 90d2570cc3c6e50b66ec1fa82d24b0eac9f08033
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
