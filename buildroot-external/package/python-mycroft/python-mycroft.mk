################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = 6f33cc0553235df483dab109778798f0e2e9fbdc
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
