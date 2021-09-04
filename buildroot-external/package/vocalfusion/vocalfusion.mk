################################################################################
#
# vocalfusion
#
################################################################################

VOCALFUSION_VERSION = c8c29036992a88726dcdfb967cbc1d9f14a95534
VOCALFUSION_SITE = $(call github,OpenVoiceOS,VocalFusionDriver,$(VOCALFUSION_VERSION))
VOCALFUSION_MODULE_SUBDIRS = driver

$(eval $(kernel-module))

define VOCALFUSION_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0644 $(@D)/xvf3510.dtbo $(BINARIES_DIR)/overlays/
endef

$(eval $(generic-package))
