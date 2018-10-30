################################################################################
#
# python-coverage
#
################################################################################

PYTHON_COVERAGE_VERSION = 4.5.1
PYTHON_COVERAGE_SOURCE = coverage-$(PYTHON_COVERAGE_VERSION).tar.gz
PYTHON_COVERAGE_SITE = https://files.pythonhosted.org/packages/35/fe/e7df7289d717426093c68d156e0fd9117c8f4872b6588e8a8928a0f68424
PYTHON_COVERAGE_SETUP_TYPE = setuptools
PYTHON_COVERAGE_LICENSE = Apache-2.0
PYTHON_COVERAGE_LICENSE_FILES = LICENSE.txt

$(eval $(python-package))
