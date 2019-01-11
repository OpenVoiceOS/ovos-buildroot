################################################################################
#
# python-padaos
#
################################################################################

PYTHON_PADAOS_VERSION = 0.1.8
PYTHON_PADAOS_SOURCE = padaos-$(PYTHON_PADAOS_VERSION).tar.gz
PYTHON_PADAOS_SITE = https://files.pythonhosted.org/packages/1b/5a/8b9053ef320f958b52c8881e0a8147faea5dd87e0fbf26958b7069ab7f76
PYTHON_PADAOS_SETUP_TYPE = setuptools

$(eval $(python-package))
