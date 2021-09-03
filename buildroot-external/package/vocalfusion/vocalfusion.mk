################################################################################
#
# vocalfusion
#
################################################################################

VOCALFUSION_VERSION = a7685b3ebb919da096f29b5b35f303b5c1a7beaf
VOCALFUSION_SITE = $(call github,OpenVoiceOS,VocalFusionDriver,$(VOCALFUSION_VERSION))
VOCALFUSION_MODULE_SUBDIRS = driver

$(eval $(kernel-module))

define VOCALFUSION_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0644 $(@D)/xvf3510.dtbo $(BINARIES_DIR)/overlays/
endef

$(eval $(generic-package))
