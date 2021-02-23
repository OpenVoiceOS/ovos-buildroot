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

$(eval $(qmake-package))
