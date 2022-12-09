################################################################################
#
# whisper-tflite
#
################################################################################

WHISPER_TFLITE_VERSION = b3649ffba57bc226492522c736b1a127e50cdc26
WHISPER_TFLITE_SITE = $(call github,usefulsensors,openai-whisper,$(WHISPER_TFLITE_VERSION))
WHISPER_TFLITE_LICENSE = Apache License 2.0
WHISPER_TFLITE_SUBDIR = tflite_minimal

WHISPER_TFLITE_INSTALL_STAGING = YES
WHISPER_TFLITE_DEPENDENCIES = host-pkgconf
WHISPER_TFLITE_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
