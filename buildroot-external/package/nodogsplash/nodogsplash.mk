################################################################################
#
# nodogsplash
#
################################################################################

NODOGSPLASH_VERSION = 3.2.1
NODOGSPLASH_SITE = $(call github,nodogsplash,nodogsplash,$(NODOGSPLASH_VERSION))
NODOGSPLASH_LICENSE = GNU General Public License v2.0
#NODOGSPLASH_AUTORECONF = YES
#NODOGSPLASH_INSTALL_STAGING = yes
NODOGSPLASH_DEPENDENCIES = libmicrohttpd

define NODOGSPLASH_BUILD_CMDS
	$(MAKE) $(TARGET_CONFIGURE_OPTS) -C $(@D) all
endef

define NODOGSPLASH_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/ndsctl $(TARGET_DIR)/usr/bin/
	$(INSTALL) -D -m 0755 $(@D)/nodogsplash $(TARGET_DIR)/usr/bin/
	mkdir -p $(TARGET_DIR)/etc/nodogsplash/htdocs/images
	$(INSTALL) -D -m 0644 $(@D)/resources/nodogsplash.conf \
		$(TARGET_DIR)/etc/nodogsplash/
	$(INSTALL) -D -m 0644 $(@D)/resources/splash.html \
                $(TARGET_DIR)/etc/nodogsplash/htdocs/
        $(INSTALL) -D -m 0644 $(@D)/resources/splash.css \
                $(TARGET_DIR)/etc/nodogsplash/htdocs/
        $(INSTALL) -D -m 0644 $(@D)/resources/status.html \
                $(TARGET_DIR)/etc/nodogsplash/htdocs/
        $(INSTALL) -D -m 0644 $(@D)/resources/splash.jpg \
                $(TARGET_DIR)/etc/nodogsplash/htdocs/images/
endef

$(eval $(generic-package))
