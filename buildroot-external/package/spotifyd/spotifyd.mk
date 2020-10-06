################################################################################
#
# spotifyd
#
################################################################################

SPOTIFYD_VERSION = v0.2.24
SPOTIFYD_SITE = $(call github,Spotifyd,spotifyd,$(SPOTIFYD_VERSION))
SPOTIFYD_LICENSE = GPL-3.0
SPOTIFYD_LICENSE_FILES = LICENSE

SPOTIFYD_DEPENDENCIES = host-cargo

SPOTIFYD_CARGO_ENV = CARGO_HOME=$(HOST_DIR)/share/cargo \
		     CC=$(TARGET_CC) \
                     HOST_CC=gcc \
		     PKG_CONFIG_ALLOW_CROSS=1 \
		     OPENSSL_LIB_DIR=$(HOST_DIR)/lib \
		     OPENSSL_INCLUDE_DIR=$(HOST_DIR)/include
SPOTIFYD_BIN_DIR = target/$(RUSTC_TARGET_NAME)/release

SPOTIFYD_CARGO_OPTS = --release \
		      --no-default-features \
		      --features=pulseaudio_backend \
		      --target=$(RUSTC_TARGET_NAME) \
		      --manifest-path=$(@D)/Cargo.toml

define SPOTIFYD_BUILD_CMDS
	$(TARGET_MAKE_ENV) $(SPOTIFYD_CARGO_ENV) rustc -V
	$(TARGET_MAKE_ENV) $(SPOTIFYD_CARGO_ENV) cargo build $(SPOTIFYD_CARGO_OPTS)
endef

define SPOTIFYD_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(@D)/$(SPOTIFYD_BIN_DIR)/spotifyd \
		$(TARGET_DIR)/usr/bin/spotifyd
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/spotifyd/spotifyd.conf \
		$(TARGET_DIR)/etc/spotifyd.conf
endef

define SPOTIFYD_INSTALL_INIT_SYSTEMD
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/spotifyd/spotifyd.service \
		$(TARGET_DIR)/usr/lib/systemd/system/spotifyd.service
endef

$(eval $(generic-package))
