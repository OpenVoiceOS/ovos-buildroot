################################################################################
#
# python-pyjokes
#
################################################################################

PYTHON_PYJOKES_VERSION = 0.6.0
PYTHON_PYJOKES_SOURCE = pyjokes-$(PYTHON_PYJOKES_VERSION).tar.gz
PYTHON_PYJOKES_SITE = https://files.pythonhosted.org/packages/c2/82/faa0a9676ba148de181793a81f193f4a5a9eb344b4faf80fa28d8b1c8f3f
PYTHON_PYJOKES_SETUP_TYPE = setuptools
PYTHON_PYJOKES_LICENSE = FIXME: please specify the exact BSD version

$(eval $(python-package))
