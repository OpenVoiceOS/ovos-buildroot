################################################################################
#
# python-nested-lookup
#
################################################################################

PYTHON_NESTED_LOOKUP_VERSION = 0.2.25
PYTHON_NESTED_LOOKUP_SOURCE = nested-lookup-$(PYTHON_NESTED_LOOKUP_VERSION).tar.gz
PYTHON_NESTED_LOOKUP_SITE = https://files.pythonhosted.org/packages/fd/42/7d6a06916aba63124eb30d2ff638cf76054f6aeea529d47f1859c3b5ccae
PYTHON_NESTED_LOOKUP_SETUP_TYPE = setuptools
PYTHON_NESTED_LOOKUP_LICENSE = Public Domain

$(eval $(python-package))
