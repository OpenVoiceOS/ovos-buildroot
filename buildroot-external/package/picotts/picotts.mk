################################################################################
#
# picotts
#
################################################################################

PICOTTS_VERSION = 21089d223e177ba3cb7e385db8613a093dff74b5
PICOTTS_SITE = $(call github,naggety,picotts,$(PICOTTS_VERSION))
PICOTTS_LICENSE = MIT
PICOTTS_LICENSE_FILES = COPYING
PICOTTS_AUTORECONF = YES
PICOTTS_SUBDIR = pico
PICOTTS_DEPENDENCIES = host-pkgconf host-automake host-autoconf host-libtool

define PICOTTS_RUN_AUTOGEN
        cd $(@D)/pico && PATH=$(BR_PATH) ./autogen.sh
endef

$(eval $(autotools-package))
