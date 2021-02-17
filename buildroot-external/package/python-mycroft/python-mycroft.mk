################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = a976bd1094dbfba155811df1ca227b40be9422ff
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
