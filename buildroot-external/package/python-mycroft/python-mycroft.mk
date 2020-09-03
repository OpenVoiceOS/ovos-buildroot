################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = 255ac428bddaebe820f9ee10e50aa08e17d2bce9
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
