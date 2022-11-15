################################################################################
#
# whispercpp
#
################################################################################

WHISPERCPP_VERSION = 83c742f1a78a018c4eac790fabab91f174d92c3a
WHISPERCPP_SITE = $(call github,ggerganov,whisper.cpp,$(WHISPERCPP_VERSION))
WHISPERCPP_LICENSE = Apache License 2.0

WHISPERCPP_INSTALL_STAGING = YES
WHISPERCPP_DEPENDENCIES = host-pkgconf
WHISPERCPP_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
