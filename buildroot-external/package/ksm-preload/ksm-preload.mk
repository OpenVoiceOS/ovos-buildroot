################################################################################
#
# ksm-preload
#
################################################################################

KSM_PRELOAD_VERSION = 459df0e8b0d4ba5ede43b7f3e244811dcbbf77f6
KSM_PRELOAD_SITE = $(call github,unbrice,ksm_preload,$(KSM_PRELOAD_VERSION))
KSM_PRELOAD_LICENSE = GPL-3.0 license

KSM_PRELOAD_INSTALL_STAGING = YES
KSM_PRELOAD_DEPENDENCIES = host-pkgconf
KSM_PRELOAD_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
