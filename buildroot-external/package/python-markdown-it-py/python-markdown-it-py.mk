################################################################################
#
# python-markdown-it-py
#
################################################################################

PYTHON_MARKDOWN_IT_PY_VERSION = 2.2.0
PYTHON_MARKDOWN_IT_PY_SOURCE = markdown-it-py-$(PYTHON_MARKDOWN_IT_PY_VERSION).tar.gz
PYTHON_MARKDOWN_IT_PY_SITE = https://files.pythonhosted.org/packages/e4/c0/59bd6d0571986f72899288a95d9d6178d0eebd70b6650f1bb3f0da90f8f7
PYTHON_MARKDOWN_IT_PY_SETUP_TYPE = setuptools

$(eval $(python-package))
