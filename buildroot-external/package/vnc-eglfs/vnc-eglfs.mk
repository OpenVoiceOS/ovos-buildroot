################################################################################
#
# vnc-eglfs
#
################################################################################

VNC_EGLFS_VERSION = e67ac4431f19e2863abedbbfa1ba76a00fe1ca92
VNC_EGLFS_SITE = $(call github,uwerat,vnc-eglfs,$(VNC_EGLFS_VERSION))
VNC_EGLFS_INSTALL_STAGING = YES

$(eval $(qmake-package))
