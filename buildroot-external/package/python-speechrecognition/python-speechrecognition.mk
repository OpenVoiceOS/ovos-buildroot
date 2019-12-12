################################################################################
#
# python-speechrecognition
#
################################################################################

PYTHON_SPEECHRECOGNITION_VERSION = 3.8.1
PYTHON_SPEECHRECOGNITION_SITE = $(call github,Uberi,speech_recognition,$(PYTHON_SPEECHRECOGNITION_VERSION))
PYTHON_SPEECHRECOGNITION_INSTALL_STAGING = YES
PYTHON_SPEECHRECOGNITION_DEPENDENCIES = flac \
					python-pyaudio \
					python-pocketsphinx \
					python-google-api-python-client 
PYTHON_SPEECHRECOGNITION_LICENSE = Apache-2.0
PYTHON_SPEECHRECOGNITION_LICENSE_FILES = LICENSE
PYTHON_SPEECHRECOGNITION_SETUP_TYPE = setuptools

$(eval $(python-package))
