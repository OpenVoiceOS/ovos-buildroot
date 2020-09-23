################################################################################
#
# python-mycroft
#
################################################################################

PYTHON_MYCROFT_VERSION = ae72ebd247f877f643573791650e63c4044604d1
PYTHON_MYCROFT_SITE = $(call github,MycroftAI,mycroft-core,$(PYTHON_MYCROFT_VERSION))
PYTHON_MYCROFT_SETUP_TYPE = setuptools
PYTHON_MYCROFT_LICENSE_FILES = LICENSE

$(eval $(python-package))
