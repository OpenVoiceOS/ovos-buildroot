################################################################################
#
# openfec
#
################################################################################

OPENFEC_VERSION = b452e08e5bb135c9fac541ce7553b7b60ceb8119
OPENFEC_SITE = $(call github,roc-streaming,openfec,$(OPENFEC_VERSION))
OPENFEC_LICENSE = MIT

OPENFEC_INSTALL_STAGING = YES
OPENFEC_DEPENDENCIES = host-pkgconf
OPENFEC_SUPPORTS_IN_SOURCE_BUILD = NO

OPENFEC_CONF_OPTS = \
	-DOPTIMIZE=DEFAULT

$(eval $(cmake-package))
