################################################################################
#
# python-pendulum
#
################################################################################

PYTHON_PENDULUM_VERSION = 2.1.2
PYTHON_PENDULUM_SOURCE = pendulum-$(PYTHON_PENDULUM_VERSION).tar.gz
PYTHON_PENDULUM_SITE = https://files.pythonhosted.org/packages/db/15/6e89ae7cde7907118769ed3d2481566d05b5fd362724025198bb95faf599
PYTHON_PENDULUM_SETUP_TYPE = setuptools
PYTHON_PENDULUM_LICENSE = MIT
PYTHON_PENDULUM_LICENSE_FILES = LICENSE

$(eval $(python-package))
