################################################################################
#
# kaldi
#
################################################################################

KALDI_VERSION = 93ef0019b847272a239fbb485ef97f29feb1d587
KALDI_SITE = $(call github,alphacep,kaldi,$(KALDI_VERSION))
KALDI_LICENSE = Apache License 2.0

KALDI_INSTALL_STAGING = YES
KALDI_DEPENDENCIES = host-pkgconf openfst lapack
KALDI_SUPPORTS_IN_SOURCE_BUILD = NO

KALDI_CONF_OPTS = \
	-DMATHLIB=OpenBLAS \
	-DKALDI_BUILD_TEST=OFF \
	-DBUILD_SHARED_LIBS=ON

$(eval $(cmake-package))
