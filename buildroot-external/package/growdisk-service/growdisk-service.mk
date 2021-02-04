################################################################################
#
# growdisk-service
#
################################################################################

GROWDISK_SERVICE_VERSION = 0.1.0
GROWDISK_SERVICE_SITE = $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/growdisk-service
GROWDISK_SERVICE_SITE_METHOD = local
GROWDISK_SERVICE_LICENSE = Apache License 2.0
GROWDISK_SERVICE_LICENSE_FILES = LICENSE

define GROWDISK_SERVICE_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 $(@D)/growdisk $(TARGET_DIR)/usr/sbin/
	$(INSTALL) -D -m 644 $(@D)/growdisk.service \
		$(TARGET_DIR)/usr/lib/systemd/system/growdisk.service
	touch $(TARGET_DIR)/etc/growdisk
endef

$(eval $(generic-package))
