################################################################################
#
# wifi-connect
#
################################################################################

WIFI_CONNECT_VERSION = ac333eb6a809b4daf3ac2e41f6c56799852caddc
WIFI_CONNECT_SITE = $(call github,balena-io,wifi-connect,$(WIFI_CONNECT_VERSION))

WIFI_CONNECT_DEPENDENCIES = host-rustc host-pkgconf

WIFI_CONNECT_CARGO_ENV = \
	PKG_CONFIG_ALLOW_CROSS=1 \
	OPENSSL_LIB_DIR=$(HOST_DIR)/lib \
	OPENSSL_INCLUDE_DIR=$(HOST_DIR)/include

WIFI_CONNECT_BIN_DIR = target/$(RUSTC_TARGET_NAME)/release

define WIFI_CONNECT_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/local/sbin
	$(INSTALL) -D -m 0755 $(@D)/$(WIFI_CONNECT_BIN_DIR)/wifi-connect \
		$(TARGET_DIR)/usr/local/sbin/wifi-connect
endef

$(eval $(cargo-package))
