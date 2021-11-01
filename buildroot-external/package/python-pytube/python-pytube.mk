################################################################################
#
# python-pytube
#
################################################################################

PYTHON_PYTUBE_VERSION = 11.0.1
PYTHON_PYTUBE_SOURCE = pytube-$(PYTHON_PYTUBE_VERSION).tar.gz
PYTHON_PYTUBE_SITE = https://files.pythonhosted.org/packages/33/0d/51a29deb2046d1d45a8b13e8b5a25307dd2fc3b49f577d5e3e563ab0fbb3
PYTHON_PYTUBE_SETUP_TYPE = setuptools
PYTHON_PYTUBE_LICENSE = The Unlicense (Unlicense)
PYTHON_PYTUBE_LICENSE_FILES = LICENSE

$(eval $(python-package))
