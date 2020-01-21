################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = aa86e10ca341143a9a5830531cc9090aa72de307
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
