################################################################################
#
# python-speech2text
#
################################################################################

PYTHON_SPEECH2TEXT_VERSION = 0.2.1
PYTHON_SPEECH2TEXT_SOURCE = speech2text-$(PYTHON_SPEECH2TEXT_VERSION).tar.gz
PYTHON_SPEECH2TEXT_SITE = https://files.pythonhosted.org/packages/a2/d9/de3f72dfc604a73a3e9b3e69c42de5cb9662e69c677e7914a4d89b528840
PYTHON_SPEECH2TEXT_SETUP_TYPE = setuptools

$(eval $(python-package))
