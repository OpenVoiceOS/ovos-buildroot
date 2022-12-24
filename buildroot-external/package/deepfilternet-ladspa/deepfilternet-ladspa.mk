################################################################################
#
# deepfilternet-ladspa
#
################################################################################

DEEPFILTERNET_LADSPA_VERSION = 27b5f07be6caba1abec7907fcca89ba906732800
DEEPFILTERNET_LADSPA_SITE = $(call github,Rikorose,DeepFilterNet,$(DEEPFILTERNET_LADSPA_VERSION))

DEEPFILTERNET_LADSPA_DEPENDENCIES = host-rustc host-pkgconf hdf5

DEEPFILTERNET_LADSPA_CARGO_ENV = PKG_CONFIG_ALLOW_CROSS=1

DEEPFILTERNET_LADSPA_BIN_DIR = target/$(RUSTC_TARGET_NAME)/release

#define DEEPFILTERNET_LADSPA_INSTALL_TARGET_CMDS
#	$(INSTALL) -D -m 0755 $(@D)/$(DEEPFILTERNET_LADSPA_BIN_DIR)/DEEPFILTERNET_LADSPA \
#		$(TARGET_DIR)/usr/bin/DEEPFILTERNET_LADSPA
#	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/DEEPFILTERNET_LADSPA/DEEPFILTERNET_LADSPA.conf \
#		$(TARGET_DIR)/etc/DEEPFILTERNET_LADSPA.conf
#endef

$(eval $(cargo-package))
