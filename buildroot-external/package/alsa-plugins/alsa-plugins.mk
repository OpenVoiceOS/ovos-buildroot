################################################################################
#
# alsa-plugins
#
################################################################################

ALSA_PLUGINS_VERSION = 1.1.9
ALSA_PLUGINS_SOURCE = alsa-plugins-$(ALSA_PLUGINS_VERSION).tar.bz2
ALSA_PLUGINS_SITE = ftp://ftp.alsa-project.org/pub/plugins
ALSA_PLUGINS_LICENSE = LGPL-2.1+ (library), GPL-2.0+ (aserver)
ALSA_PLUGINS_LICENSE_FILES = COPYING aserver/COPYING
ALSA_PLUGINS_CFLAGS = $(TARGET_CFLAGS)
ALSA_PLUGINS_AUTORECONF = YES
ALSA_PLUGINS_DEPENDENCIES = alsa-lib libsamplerate pulseaudio
ALSA_PLUGINS_CONF_OPTS = \
	--with-plugindir=/usr/lib/alsa-lib \
	--localstatedir=/var \
	--disable-jack \
	--enable-samplerate \
	--enable-pulseaudio \
	--disable-avcodec \
	--with-speex=builtin

$(eval $(autotools-package))
