################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = 17840decd5e1ca52282bfe1c63b82bb16acf4042
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
