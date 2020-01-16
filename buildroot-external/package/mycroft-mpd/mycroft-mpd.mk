################################################################################
#
# mycroft-mpd
#
################################################################################

define MYCROFT_MPD_INSTALL_EXTRA_FILES
	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_MYCROFTOS_PATH)/package/mycroft-mpd/mpd.conf \
		$(TARGET_DIR)/etc/mpd.conf

	mkdir -p $(TARGET_DIR)/opt/mpd/playlists
	mkdir -p $(TARGET_DIR)/opt/mpd/music
	mkdir -p $(TARGET_DIR)/var/lib/mpd

	cp -r $(BR2_EXTERNAL_MYCROFTOS_PATH)/package/mycroft-mpd/playlists/* \
		$(TARGET_DIR)/opt/mpd/playlists/

	$(INSTALL) -m 0644 -D $(BR2_EXTERNAL_MYCROFTOS_PATH)/package/mycroft-mpd/mpd.service \
                $(TARGET_DIR)/usr/lib/systemd/system/mpd.service
endef

MYCROFT_MPD_POST_INSTALL_TARGET_HOOKS += MYCROFT_MPD_INSTALL_EXTRA_FILES

$(eval $(generic-package))
