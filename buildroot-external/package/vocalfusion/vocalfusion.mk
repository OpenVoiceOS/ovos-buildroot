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

	$(INSTALL) -D -m 755 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/vocalfusion/xvf3510-flash \
                $(TARGET_DIR)/usr/sbin/xvf3510-flash

	mkdir -p $(TARGET_DIR)/usr/lib/firmware/xvf3510
	$(INSTALL) -D -m 0644 $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/vocalfusion/app_xvf3510_int_spi_boot_v4_1_0.bin \
                $(TARGET_DIR)/usr/lib/firmware/xvf3510/app_xvf3510_int_spi_boot_v4_1_0.bin
endef

$(eval $(generic-package))
