################################################################################
#
# python-pymplayer
#
################################################################################

PYTHON_PYMPLAYER_VERSION = eaa0a1dbfc60cb0f4f1b3e495d665714c089474a
PYTHON_PYMPLAYER_SITE = https://github.com/JarbasAl/py_mplayer.git
PYTHON_PYMPLAYER_SITE_METHOD = git
PYTHON_PYMPLAYER_SETUP_TYPE = distutils
PYTHON_PYMPLAYER_LICENSE = MIT

$(eval $(python-package))
