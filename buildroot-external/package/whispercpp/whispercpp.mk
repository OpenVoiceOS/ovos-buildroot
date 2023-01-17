################################################################################
#
# whispercpp
#
################################################################################

WHISPERCPP_VERSION = 8738427dd60bda894df1ff3c12317cca2e960016
WHISPERCPP_SITE = $(call github,ggerganov,whisper.cpp,$(WHISPERCPP_VERSION))
WHISPERCPP_LICENSE = Apache License 2.0

WHISPERCPP_INSTALL_STAGING = YES
WHISPERCPP_DEPENDENCIES = host-pkgconf
WHISPERCPP_SUPPORTS_IN_SOURCE_BUILD = NO

WHISPERCPP_CONF_OPTS = \
	-DBUILD_SHARED_LIBS_DEFAULT=ON \
	-DWHISPER_SUPPORT_OPENBLAS=ON \
	-DWHISPER_BUILD_TESTS=ON \
	-DWHISPER_BUILD_EXAMPLES=ON \
	-DWHISPER_SUPPORT_SDL2=ON

WHISPERCPP_POST_INSTALL_TARGET_HOOKS = WHISPERCPP_INSTALL_BINS

define WHISPERCPP_INSTALL_BINS
	mkdir -p $(TARGET_DIR)/usr/bin/whispercpp
	$(INSTALL) -D -m 755 $(@D)/buildroot-build/bin/* \
		$(TARGET_DIR)/usr/bin/whispercpp/
endef

$(eval $(cmake-package))
