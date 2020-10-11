#############################################################
#
# libcanberra
#
#############################################################

LIBCANBERRA_VERSION = 0.30
LIBCANBERRA_SOURCE = libcanberra-$(LIBCANBERRA_VERSION).tar.xz
LIBCANBERRA_SITE = http://0pointer.de/lennart/projects/libcanberra
LIBCANBERRA_INSTALL_STAGING = YES
LIBCANBERRA_DEPENDENCIES = libvorbis libtool alsa-lib
LIBCANBERRA_CONF_OPTS += --disable-oss
LIBCANBERRA_LICENSE = LGPLv2.1+
LIBCANBERRA_LICENSE_FILES = LGPL

$(eval $(autotools-package))
