################################################################################
#
# openfst
#
################################################################################

OPENFST_VERSION = 7dfd808194105162f20084bb4d8e4ee4b65266d5
OPENFST_SITE = $(call github,alphacep,openfst,$(OPENFST_VERSION))
OPENFST_LICENSE = Apache License 2.0

OPENFST_INSTALL_STAGING = YES

OPENFST_AUTORECONF = YES
OPENFST_CONF_OPTS = \
	--enable-static \
	--enable-shared \
	--enable-far \
	--enable-ngram-fsts \
	--enable-lookahead-fsts \
	--with-pic \
	--disable-bin

$(eval $(autotools-package))
