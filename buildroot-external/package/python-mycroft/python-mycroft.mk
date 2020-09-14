################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = 31fd9914efc7b9513adc50016b148513d56fb2f3
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
