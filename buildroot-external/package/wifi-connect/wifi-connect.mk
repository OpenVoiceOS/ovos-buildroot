################################################################################
#
# wifi-connect
#
################################################################################

WIFI_CONNECT_VERSION = 57f8f4a7190dfcdd0a7c7127d298378249f95135
WIFI_CONNECT_SITE = $(call github,balena-os,wifi-connect,$(WIFI_CONNECT_VERSION))
WIFI_CONNECT_DEPENDENCIES = host-rustc host-pkgconf

WIFI_CONNECT_CARGO_ENV = PKG_CONFIG_ALLOW_CROSS=1

define WIFI_CONNECT_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/local/sbin
	$(INSTALL) -D -m 0755 $(@D)/target/$(RUSTC_TARGET_NAME)/release/wifi-connect \
		$(TARGET_DIR)/usr/local/sbin/wifi-connect
endef

$(eval $(cargo-package))
