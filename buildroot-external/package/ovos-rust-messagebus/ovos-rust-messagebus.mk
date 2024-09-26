################################################################################
#
# ovos-rust-messagebus
#
################################################################################

OVOS_RUST_MESSAGEBUS_VERSION = 0.3.1
OVOS_RUST_MESSAGEBUS_SITE = $(call github,OscillateLabsLLC,ovos-rust-messagebus,v$(OVOS_RUST_MESSAGEBUS_VERSION))
OVOS_RUST_MESSAGEBUS_DEPENDENCIES = host-rustc host-pkgconf

OVOS_RUST_MESSAGEBUS_CARGO_ENV = PKG_CONFIG_ALLOW_CROSS=1

define OVOS_RUST_MESSAGEBUS_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/local/bin
	$(INSTALL) -D -m 0755 $(@D)/target/$(RUSTC_TARGET_NAME)/release/ovos_messagebus \
		$(TARGET_DIR)/usr/local/bin/ovos_messagebus
endef

$(eval $(cargo-package))
