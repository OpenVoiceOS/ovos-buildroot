################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = b746f365c91098a40f389d0c277a5513031c51d5
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
