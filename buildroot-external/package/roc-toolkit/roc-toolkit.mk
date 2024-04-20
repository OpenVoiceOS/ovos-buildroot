################################################################################
#
# roc-toolkit
#
################################################################################

ROC_TOOLKIT_VERSION = 0.3.0
ROC_TOOLKIT_SITE = $(call github,roc-streaming,roc-toolkit,v$(ROC_TOOLKIT_VERSION))
ROC_TOOLKIT_LICENSE = MPL-2.0
ROC_TOOLKIT_LICENSE_FILES = LICENSE
ROC_TOOLKIT_INSTALL_STAGING = YES

ROC_TOOLKIT_DEPENDENCIES = \
	host-scons \
	host-pkgconf \
	host-ragel \
	host-gengetopt \
	gst1-libav \
	libunwind \
	openfec \
	speexdsp \
	sox \
	pulseaudio \
	libuv

define ROC_TOOLKIT_BUILD_CMDS
	(cd $(@D); \
	$(TARGET_CONFIGURE_OPTS) CROSS=$(TARGET_CROSS) \
		$(SCONS) $(ROCTOOLKIT__SCONS_OPTS))
endef

define ROC_TOOLKIT_INSTALL_STAGING_CMDS
	(cd $(@D); \
	$(TARGET_CONFIGURE_OPTS) CROSS=$(TARGET_CROSS) \
		$(SCONS) --prefix="$(STAGING_DIR)/usr" install)
endef

define ROC_TOOLKIT_INSTALL_TARGET_CMDS
	(cd $(@D); \
	$(TARGET_CONFIGURE_OPTS) CROSS=$(TARGET_CROSS) \
		$(SCONS) --prefix="$(TARGET_DIR)/usr" install)
endef

$(eval $(generic-package))
