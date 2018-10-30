################################################################################
#
# python-monotonic
#
################################################################################

PYTHON_MONOTONIC_VERSION = 1.5
PYTHON_MONOTONIC_SOURCE = monotonic-$(PYTHON_MONOTONIC_VERSION).tar.gz
PYTHON_MONOTONIC_SITE = https://files.pythonhosted.org/packages/19/c1/27f722aaaaf98786a1b338b78cf60960d9fe4849825b071f4e300da29589
PYTHON_MONOTONIC_SETUP_TYPE = setuptools
PYTHON_MONOTONIC_LICENSE = Apache-2.0
PYTHON_MONOTONIC_LICENSE_FILES = LICENSE

$(eval $(python-package))
