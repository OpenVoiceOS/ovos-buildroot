################################################################################
#
# whispercpp
#
################################################################################

WHISPERCPP_VERSION = aa6adda26e1ee9843dddb013890e3312bee52cfe
WHISPERCPP_SITE = $(call github,ggerganov,whisper.cpp,$(WHISPERCPP_VERSION))
WHISPERCPP_LICENSE = Apache License 2.0

WHISPERCPP_INSTALL_STAGING = YES
WHISPERCPP_DEPENDENCIES = host-pkgconf
WHISPERCPP_SUPPORTS_IN_SOURCE_BUILD = NO

WHISPERCPP_CONF_OPTS = \
	-DBUILD_SHARED_LIBS_DEFAULT=ON \
	-DWHISPER_SUPPORT_OPENBLAS=ON

$(eval $(cmake-package))
