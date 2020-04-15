################################################################################
#
# prepare_system-service
#
################################################################################

PREPARE_SYSTEM_SERVICE_VERSION = 0.1.0
PREPARE_SYSTEM_SERVICE_SITE = $(BR2_EXTERNAL_MYCROFTOS_PATH)/package/prepare_system-service
PREPARE_SYSTEM_SERVICE_SITE_METHOD = local
PREPARE_SYSTEM_SERVICE_LICENSE = Apache License 2.0
PREPARE_SYSTEM_SERVICE_LICENSE_FILES = LICENSE

define PREPARE_SYSTEM_SERVICE_INSTALL_TARGET_CMDS
	$(INSTALL) -m 0755 $(@D)/prepare_system $(TARGET_DIR)/usr/sbin/
	$(INSTALL) -D -m 644 $(@D)/prepare_system.service \
		$(TARGET_DIR)/usr/lib/systemd/system/prepare_system.service
endef

$(eval $(generic-package))
