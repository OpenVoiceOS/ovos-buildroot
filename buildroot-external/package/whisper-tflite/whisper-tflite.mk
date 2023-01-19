################################################################################
#
# whisper-tflite
#
################################################################################

WHISPER_TFLITE_VERSION = f11d55e440c9f8d51782ef8badf2270583486000
WHISPER_TFLITE_SITE = $(call github,usefulsensors,openai-whisper,$(WHISPER_TFLITE_VERSION))
WHISPER_TFLITE_LICENSE = Apache License 2.0
WHISPER_TFLITE_SUBDIR = tflite_minimal

WHISPER_TFLITE_INSTALL_STAGING = YES
WHISPER_TFLITE_DEPENDENCIES = host-pkgconf
WHISPER_TFLITE_SUPPORTS_IN_SOURCE_BUILD = NO

WHISPER_TFLITE_PRE_CONFIGURE_HOOKS = WHISPER_TFLITE_MEDIUM_MODEL

define WHISPER_TFLITE_MEDIUM_MODEL
	cp $(@D)/models/filters_vocab_multilingual.bin $(@D)/$(WHISPER_TFLITE_SUBDIR)/filters_vocab_gen.bin
endef

$(eval $(cmake-package))
