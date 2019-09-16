################################################################################
#
# python-casttube
#
################################################################################

PYTHON_CASTTUBE_VERSION = 0.2.0
PYTHON_CASTTUBE_SOURCE = casttube-$(PYTHON_CASTTUBE_VERSION).tar.gz
PYTHON_CASTTUBE_SITE = https://files.pythonhosted.org/packages/54/d1/8edc98ef2aa08eed8dd72e2ef31b6658ba222ea8d228a4c2c3e73a58991a
PYTHON_CASTTUBE_SETUP_TYPE = setuptools

$(eval $(python-package))
