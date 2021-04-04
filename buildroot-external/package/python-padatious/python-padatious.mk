################################################################################
#
# python-padatious
#
################################################################################

PYTHON_PADATIOUS_VERSION =311b905683290cce6623251b4b53e43e6f83d5bb
PYTHON_PADATIOUS_SITE = $(call github,MycroftAI,padatious,$(PYTHON_PADATIOUS_VERSION))
PYTHON_PADATIOUS_SETUP_TYPE = setuptools
PYTHON_PADATIOUS_LICENSE_FILES = LICENSE

$(eval $(python-package))
