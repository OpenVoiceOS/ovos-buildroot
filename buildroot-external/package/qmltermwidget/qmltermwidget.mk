################################################################################
#
# qmltermwidget
#
################################################################################

QMLTERMWIDGET_VERSION = 63228027e1f97c24abb907550b22ee91836929c5
QMLTERMWIDGET_SITE = $(call github,Swordfish90,qmltermwidget,$(QMLTERMWIDGET_VERSION))
QMLTERMWIDGET_LICENSE = GPL-2.0
QMLTERMWIDGET_LICENSE_FILES = LICENSE
#QMLTERMWIDGET_INSTALL_STAGING = YES

QMLTERMWIDGET_POST_CONFIGURE_HOOKS = QMLTERMWIDGET_QML_SETUP

define QMLTERMWIDGET_QML_SETUP
	cp -r $(@D)/src/qmldir \
	$(@D)/lib/kb-layouts \
	$(@D)/lib/color-schemes \
	$(@D)/src/QMLTermScrollbar.qml \
	$(TARGET_DIR)/usr/qml/QMLTermWidget
endef

define QMLTERMWIDGET_INSTALL_TARGET_CMDS
	$(TARGET_MAKE_ENV) $(MAKE) -C $(@D) install INSTALL_ROOT=$(TARGET_DIR)
	rm -Rf $(TARGET_DIR)/usr/mkspecs
endef

$(eval $(qmake-package))
