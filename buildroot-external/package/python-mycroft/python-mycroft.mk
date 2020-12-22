################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = 4c254aa99f11bb9c027c728908198a3376cd39f3
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
