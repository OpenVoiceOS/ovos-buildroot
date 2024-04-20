################################################################################
#
# spotifyd
#
################################################################################

SPOTIFYD_VERSION = 0.3.5
SPOTIFYD_SITE = $(call github,Spotifyd,spotifyd,v$(SPOTIFYD_VERSION))
SPOTIFYD_LICENSE = GPL-3.0
SPOTIFYD_LICENSE_FILES = LICENSE

SPOTIFYD_DEPENDENCIES = host-rustc host-pkgconf

SPOTIFYD_CARGO_ENV = \
	PKG_CONFIG_ALLOW_CROSS=1 \
	OPENSSL_LIB_DIR=$(HOST_DIR)/lib \
        OPENSSL_INCLUDE_DIR=$(HOST_DIR)/include

SPOTIFYD_BIN_DIR = target/$(RUSTC_TARGET_NAME)/release

SPOTIFYD_CARGO_BUILD_OPTS = --no-default-features \
		      --features=pulseaudio_backend,dbus_keyring,dbus_mpris

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

$(eval $(cargo-package))
