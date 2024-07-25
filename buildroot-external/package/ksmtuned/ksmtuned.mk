################################################################################
#
# ksmtuned
#
################################################################################

KSMTUNED_VERSION = 018d0ed5876aee27b106c46c8889780d89ddcca2
KSMTUNED_SITE = $(call github,ksmtuned,ksmtuned,$(KSMTUNED_VERSION))
KSMTUNED_LICENSE = GPL-2.0 license

KSMTUNED_INSTALL_STAGING = NO
KSMTUNED_DEPENDENCIES = host-pkgconf

$(eval $(meson-package))
