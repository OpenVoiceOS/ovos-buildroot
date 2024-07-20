################################################################################
#
# python-ovos-utils
#
################################################################################

PYTHON_OVOS_UTILS_VERSION = 0.1.0a24
PYTHON_OVOS_UTILS_SOURCE = ovos_utils-$(PYTHON_OVOS_UTILS_VERSION).tar.gz
PYTHON_OVOS_UTILS_SITE = https://files.pythonhosted.org/packages/2a/fb/ad024a77ad33941b5a51d1e073710d4d458faea21521612a3e45545c5b19
PYTHON_OVOS_UTILS_SETUP_TYPE = setuptools
PYTHON_OVOS_UTILS_LICENSE_FILES = LICENSE
PYTHON_OVOS_UTILS_ENV = MYCROFT_LOOSE_REQUIREMENTS=true

$(eval $(python-package))
