################################################################################
#
# mycroft-gui
#
################################################################################

MYCROFT_GUI_VERSION = cb734266ba1f3accaa158507008206620a3c2dde
MYCROFT_GUI_SITE = git://github.com/MycroftAI/mycroft-gui-mark-2.git
MYCROFT_GUI_LICENSE = Apache License 2.0
MYCROFT_GUI_AUTORECONF = YES
MYCROFT_GUI_INSTALL_STAGING = YES
#MYCROFT_GUI_DEPENDENCIES = host-pkgconf host-automake host-autoconf host-libtool

$(eval $(cmake-package))
