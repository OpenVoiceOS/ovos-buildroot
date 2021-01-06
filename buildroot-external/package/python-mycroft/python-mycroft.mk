################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = 81eae60b61071746d3f5837c1fe5b8b64ecd0e64
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
