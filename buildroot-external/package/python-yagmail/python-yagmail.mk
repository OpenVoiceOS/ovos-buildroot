################################################################################
#
# python-yagmail
#
################################################################################

PYTHON_YAGMAIL_VERSION = 0.14.260
PYTHON_YAGMAIL_SOURCE = yagmail-$(PYTHON_YAGMAIL_VERSION).tar.gz
PYTHON_YAGMAIL_SITE = https://files.pythonhosted.org/packages/74/64/f76a06d307f07cc449d0747269ce1787e6a5cc7d986d1331c319d05fbb16
PYTHON_YAGMAIL_SETUP_TYPE = setuptools
PYTHON_YAGMAIL_LICENSE = MIT
PYTHON_YAGMAIL_LICENSE_FILES = LICENSE

$(eval $(python-package))
