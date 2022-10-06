################################################################################
#
# python-user-agents
#
################################################################################

PYTHON_USER_AGENTS_VERSION = 2.2.0
PYTHON_USER_AGENTS_SOURCE = user-agents-$(PYTHON_USER_AGENTS_VERSION).tar.gz
PYTHON_USER_AGENTS_SITE = https://files.pythonhosted.org/packages/e3/e1/63c5bfb485a945010c8cbc7a52f85573561737648d36b30394248730a7bc
PYTHON_USER_AGENTS_SETUP_TYPE = setuptools
PYTHON_USER_AGENTS_LICENSE = MIT
PYTHON_USER_AGENTS_LICENSE_FILES = LICENSE.txt

$(eval $(python-package))
