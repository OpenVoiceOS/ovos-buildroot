################################################################################
#
# deepfilternet-ladspa
#
################################################################################

DEEPFILTERNET_LADSPA_VERSION = 27b5f07be6caba1abec7907fcca89ba906732800
DEEPFILTERNET_LADSPA_SITE = $(call github,Rikorose,DeepFilterNet,$(DEEPFILTERNET_LADSPA_VERSION))
DEEPFILTERNET_LADSPA_SUBDIR = ladspa
DEEPFILTERNET_LADSPA_DEPENDENCIES = host-rustc host-pkgconf hdf5

DEEPFILTERNET_LADSPA_CARGO_ENV = PKG_CONFIG_ALLOW_CROSS=1

DEEPFILTERNET_LADSPA_BIN_DIR = target/$(RUSTC_TARGET_NAME)/release

define DEEPFILTERNET_LADSPA_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/usr/lib/ladspa
	$(INSTALL) -D -m 0644 $(@D)/$(DEEPFILTERNET_LADSPA_BIN_DIR)/libdeep_filter_ladspa.so \
		$(TARGET_DIR)/usr/lib/ladspa/libdeep_filter_ladspa.so
endef

$(eval $(cargo-package))
