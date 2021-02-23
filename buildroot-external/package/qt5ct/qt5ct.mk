################################################################################
#
# qt5ct
#
################################################################################

QT5CT_VERSION = 587
QT5CT_SITE = https://svn.code.sf.net/p/qt5ct/code/trunk
QT5CT_SITE_METHOD = svn
QT5CT_SUBDIR = qt5ct
QT5CT_CONF_OPTS = LRELEASE_EXECUTABLE=$(HOST_DIR)/usr/bin/lrelease \
		  PREFIX=$(TARGET_DIR)/usr/share

define QT5CT_COPY_FILES
	mkdir -p $(TARGET_DIR)/usr/share/qt5ct
	$(INSTALL) -D -m 755 $(@D)/qt5cttmp-target-install/$(TARGET_DIR)/usr/share/bin/qt5ct \
                $(TARGET_DIR)/usr/bin/qt5ct
	mkdir -p $(TARGET_DIR)/usr/share/applications
	$(INSTALL) -D -m 644 $(@D)/qt5cttmp-target-install/$(TARGET_DIR)/usr/share/share/applications/qt5ct.desktop \
		$(TARGET_DIR)/usr/share/applications/qt5ct.desktop
	mkdir -p $(TARGET_DIR)/usr/share/qt5ct/colors
	mkdir -p $(TARGET_DIR)/usr/share/qt5ct/qss
	$(INSTALL) -D -m 644 $(@D)/qt5cttmp-target-install/$(TARGET_DIR)/usr/share/share/qt5ct/colors/* \
		$(TARGET_DIR)/usr/share/qt5ct/colors/
	$(INSTALL) -D -m 644 $(@D)/qt5cttmp-target-install/$(TARGET_DIR)/usr/share/share/qt5ct/qss/* \
                $(TARGET_DIR)/usr/share/qt5ct/qss/
endef

QT5CT_POST_INSTALL_TARGET_HOOKS += QT5CT_COPY_FILES

$(eval $(qmake-package))
