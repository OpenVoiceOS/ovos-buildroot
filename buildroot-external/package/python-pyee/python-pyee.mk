################################################################################
#
# python-pyee
#
################################################################################

PYTHON_PYEE_VERSION = 5.0.0
PYTHON_PYEE_SOURCE = pyee-$(PYTHON_PYEE_VERSION).tar.gz
PYTHON_PYEE_SITE = https://files.pythonhosted.org/packages/c6/35/b37e4ffbf46063c883675e028e38e2a24b67433fd587f188e2a5005d9329
PYTHON_PYEE_SETUP_TYPE = distutils
PYTHON_PYEE_LICENSE = MIT

$(eval $(python-package))
