################################################################################
#
# vocalfusion
#
################################################################################

VOCALFUSION_VERSION = d496d45b715200776b39633013746574694a98ea
VOCALFUSION_SITE = $(call github,OpenVoiceOS,VocalFusionDriver,$(VOCALFUSION_VERSION))
VOCALFUSION_MODULE_SUBDIRS = driver

$(eval $(kernel-module))

define VOCALFUSION_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0644 $(@D)/xvf3510.dtbo $(BINARIES_DIR)/overlays/
endef

$(eval $(generic-package))
