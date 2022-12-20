################################################################################
#
# vosk-api
#
################################################################################

VOSK_API_VERSION = cf2560c9f8a49d3d366b433fdabd78c518231bec
VOSK_API_SITE = $(call github,alphacep,vosk-api,$(VOSK_API_VERSION))
VOSK_API_LICENSE = Apache License 2.0

VOSK_API_INSTALL_STAGING = YES
VOSK_API_DEPENDENCIES = host-pkgconf kaldi

VOSK_API_CONF_OPTS += \
	-DCMAKE_C_FLAGS="$(TARGET_CFLAGS) \
		-I$(STAGING_DIR)/usr/include/kaldi" \
	-DCMAKE_CXX_FLAGS="$(TARGET_CXXFLAGS) \
		-I$(STAGING_DIR)/usr/include/kaldi"

$(eval $(cmake-package))
