################################################################################
#
# wifisetup-service
#
################################################################################

WIFISETUP_SERVICE_VERSION = 0.1.0
WIFISETUP_SERVICE_SITE = $(BR2_EXTERNAL_MYCROFTOS_PATH)/package/wifisetup-service
WIFISETUP_SERVICE_SITE_METHOD = local
WIFISETUP_SERVICE_LICENSE = Apache License 2.0
WIFISETUP_SERVICE_LICENSE_FILES = LICENSE

define WIFISETUP_SERVICE_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 644 $(@D)/mycroftos-wifisetup.service \
		$(TARGET_DIR)/usr/lib/systemd/system/mycroftos-wifisetup.service
	mkdir -p $(TARGET_DIR)/etc/systemd/system/multi-user.target.wants
	ln -fs ../../../../usr/lib/systemd/system/mycroftos-wifisetup.service \
		$(TARGET_DIR)/etc/systemd/system/multi-user.target.wants/mycroftos-wifisetup.service
endef

$(eval $(generic-package))
