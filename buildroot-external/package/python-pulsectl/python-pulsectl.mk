################################################################################
#
# python-pulsectl
#
################################################################################

PYTHON_PULSECTL_VERSION = 17.7.4
PYTHON_PULSECTL_SOURCE = pulsectl-$(PYTHON_PULSECTL_VERSION).tar.gz
PYTHON_PULSECTL_SITE = https://files.pythonhosted.org/packages/ed/14/4734e40340ab115e53762617c8fa654255e1b6e0d72c129e47f78a02429f
PYTHON_PULSECTL_SETUP_TYPE = setuptools
PYTHON_PULSECTL_LICENSE = MIT
PYTHON_PULSECTL_LICENSE_FILES = COPYING

$(eval $(python-package))
