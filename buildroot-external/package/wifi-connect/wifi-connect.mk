################################################################################
#
# wifi-connect
#
################################################################################

WIFI_CONNECT_VERSION = ce951054c8038c7d08a37a516c5e55f903e065ac
WIFI_CONNECT_SITE = $(call github,balena-os,wifi-connect,$(WIFI_CONNECT_VERSION))
WIFI_CONNECT_DEPENDENCIES = host-rustc host-pkgconf

WIFI_CONNECT_CARGO_ENV = PKG_CONFIG_ALLOW_CROSS=1

define WIFI_CONNECT_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/local/sbin
	$(INSTALL) -D -m 0755 $(@D)/target/$(RUSTC_TARGET_NAME)/release/wifi-connect \
		$(TARGET_DIR)/usr/local/sbin/wifi-connect
endef

$(eval $(cargo-package))
