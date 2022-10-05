################################################################################
#
# python-pyaudio
#
################################################################################

PYTHON_PYAUDIO_VERSION = 0.2.12
PYTHON_PYAUDIO_SOURCE = PyAudio-$(PYTHON_PYAUDIO_VERSION).tar.gz
PYTHON_PYAUDIO_SITE = https://files.pythonhosted.org/packages/3e/2f/67dc1505002ed6a4ef3f5941d6f07209d4c013a0271dd8d18314f54f6bf0
PYTHON_PYAUDIO_SETUP_TYPE = setuptools
PYTHON_PYAUDIO_LICENSE = 

$(eval $(python-package))
