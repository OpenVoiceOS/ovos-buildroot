################################################################################
#
# python-jaraco-text
#
################################################################################

PYTHON_JARACO_TEXT_VERSION = 3.11.1
PYTHON_JARACO_TEXT_SOURCE = jaraco.text-$(PYTHON_JARACO_TEXT_VERSION).tar.gz
PYTHON_JARACO_TEXT_SITE = https://files.pythonhosted.org/packages/cd/32/2d0656905672c06c830dd1c85d11c5edbd5203f7ef6522f7c080a95c3470
PYTHON_JARACO_TEXT_LICENSE = MIT
PYTHON_JARACO_TEXT_LICENSE_FILES = LICENSE
PYTHON_JARACO_TEXT_SETUP_TYPE = setuptools
PYTHON_JARACO_TEXT_DEPENDENCIES = host-python-setuptools-scm

$(eval $(python-package))
