################################################################################
#
# whispercpp
#
################################################################################

WHISPERCPP_VERSION = c23588cc4b2c4be4ba3634a21c7f2b302c5f370e
WHISPERCPP_SITE = $(call github,ggerganov,whisper.cpp,$(WHISPERCPP_VERSION))
WHISPERCPP_LICENSE = Apache License 2.0

WHISPERCPP_INSTALL_STAGING = YES
WHISPERCPP_DEPENDENCIES = host-pkgconf
WHISPERCPP_SUPPORTS_IN_SOURCE_BUILD = NO

WHISPERCPP_CONF_OPTS = \
	-DBUILD_SHARED_LIBS_DEFAULT=ON \
	-DWHISPER_BUILD_TESTS=ON \
	-DWHISPER_BUILD_EXAMPLES=ON

ifeq ($(BR2_PACKAGE_OPENBLAS),y)
	WHISPERCPP_DEPENDENCIES += openblas
	WHISPERCPP_CONF_OPTS += -DWHISPER_SUPPORT_OPENBLAS=ON
endif

ifeq ($(BR2_PACKAGE_SDL2),y)
        WHISPERCPP_DEPENDENCIES += sdl2
        WHISPERCPP_CONF_OPTS += -DWHISPER_SUPPORT_SDL2=ON
endif

WHISPERCPP_POST_INSTALL_TARGET_HOOKS = WHISPERCPP_INSTALL_BINS

define WHISPERCPP_INSTALL_BINS
	mkdir -p $(TARGET_DIR)/usr/bin/whispercpp
	$(INSTALL) -D -m 755 $(@D)/buildroot-build/bin/* \
		$(TARGET_DIR)/usr/bin/whispercpp/
endef

$(eval $(cmake-package))
