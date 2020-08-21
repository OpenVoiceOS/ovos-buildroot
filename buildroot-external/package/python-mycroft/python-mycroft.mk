################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = 305623acd87e868797bf4988684b3c9f23147a0f
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
