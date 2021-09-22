################################################################################
#
# ovos-dashboard
#
################################################################################

OVOS_DASHBOARD_VERSION = 0e311a5ca9aeaa19bcc8a3aec83fb254dc30c152
OVOS_DASHBOARD_SITE = git://github.com/OpenVoiceOS/OVOS-Dashboard
OVOS_DASHBOARD_SITE_METHOD = git
OVOS_DASHBOARD_LOCATION = usr/local/share/ovos-dashboard

define OVOS_DASHBOARD_INSTALL_TARGET_CMDS
	mkdir -p $(TARGET_DIR)/$(OVOS_DASHBOARD_LOCATION)
	cp -dpfr $(@D)/* $(TARGET_DIR)/$(OVOS_DASHBOARD_LOCATION)

	mkdir -p $(TARGET_DIR)/home/mycroft/.config/systemd/user
	cp -dpfr $(BR2_EXTERNAL_OPENVOICEOS_PATH)/package/ovos-dashboard/ovos-dashboard@.service \
        $(TARGET_DIR)/home/mycroft/.config/systemd/user/ovos-dashboard@.service
endef

$(eval $(generic-package))
