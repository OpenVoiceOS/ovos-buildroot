################################################################################
#
# whispercpp
#
################################################################################

WHISPERCPP_VERSION = d6b84b2a23220dd8b8792872a3ab6802cd24b424
WHISPERCPP_SITE = $(call github,ggerganov,whisper.cpp,$(WHISPERCPP_VERSION))
WHISPERCPP_LICENSE = Apache License 2.0

WHISPERCPP_INSTALL_STAGING = YES
WHISPERCPP_DEPENDENCIES = host-pkgconf
WHISPERCPP_SUPPORTS_IN_SOURCE_BUILD = NO

$(eval $(cmake-package))
