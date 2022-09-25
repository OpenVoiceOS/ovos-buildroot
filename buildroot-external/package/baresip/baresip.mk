#############################################################
#
# BARESIP
#
#############################################################

BARESIP_VERSION = 2.7.0
BARESIP_SOURCE = v$(BARESIP_VERSION).tar.gz
BARESIP_SITE = https://github.com/baresip/baresip/archive
BARESIP_DEPENDENCIES = libre librem zlib

ifeq ($(BR2_PACKAGE_ALSA_LIB),y)
BARESIP_DEPENDENCIES += alsa-lib
endif

ifeq ($(BR2_PACKAGE_FFMPEG_SWSCALE),y)
BARESIP_DEPENDENCIES += ffmpeg
endif

ifeq ($(BR2_PACKAGE_LIBSNDFILE),y)
BARESIP_DEPENDENCIES += libsndfile
endif

ifeq ($(BR2_PACKAGE_SPEEX),y)
BARESIP_DEPENDENCIES += speex
endif

ifeq ($(BR2_PACKAGE_UTIL_LINUX_LIBUUID),y)
BARESIP_DEPENDENCIES += util-linux
endif

ifeq ($(BR2_PACKAGE_XORG7),y)
BARESIP_DEPENDENCIES += xlib_libXext
endif

$(eval $(cmake-package))
