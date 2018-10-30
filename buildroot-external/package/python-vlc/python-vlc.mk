################################################################################
#
# python-vlc
#
################################################################################

PYTHON_VLC_VERSION = 1.1.2
PYTHON_VLC_SOURCE = python-vlc-$(PYTHON_VLC_VERSION).tar.gz
PYTHON_VLC_SITE = https://files.pythonhosted.org/packages/43/ea/f2726b9eca7ded969d9671c583d5079f2486b8d3454f4e9d6649e0455909
PYTHON_VLC_SETUP_TYPE = setuptools
PYTHON_VLC_LICENSE = LGPL-2.1
PYTHON_VLC_LICENSE_FILES = COPYING

$(eval $(python-package))
