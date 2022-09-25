################################################################################
#
# wifi-connect
#
################################################################################

WIFI_CONNECT_VERSION = 3051c591c96cc129d4eadcea2d2761448ca32b7a
WIFI_CONNECT_SITE = $(call github,balena-io,wifi-connect,$(WIFI_CONNECT_VERSION))
WIFI_CONNECT_DEPENDENCIES = host-rustc host-pkgconf

WIFI_CONNECT_CARGO_ENV = PKG_CONFIG_ALLOW_CROSS=1 \
	CARGO_HOME=$(HOST_DIR)/share/cargo \
	RUST_TARGET_PATH=$(HOST_DIR)/etc/rustc \
	TARGET_CC=$(TARGET_CC) \
	CC=$(TARGET_CC)

WIFI_CONNECT_CARGO_OPTS = --target=${RUSTC_TARGET_NAME} \
	--manifest-path=$(@D)/Cargo.toml \
	--release

define WIFI_CONNECT_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(WIFI_CONNECT_CARGO_ENV) \
		cargo build $(WIFI_CONNECT_CARGO_OPTS)
endef

define WIFI_CONNECT_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/local/sbin
	$(INSTALL) -D -m 0755 $(@D)/$(RUSTC_TARGET_NAME)/release/wifi-connect \
		$(TARGET_DIR)/usr/local/sbin/wifi-connect
endef

$(eval $(generic-package))
