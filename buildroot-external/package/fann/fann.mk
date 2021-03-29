################################################################################
#
# fann
#
################################################################################

FANN_VERSION = a3cd24e528d6a865915a4fed6e8fac164ff8bfdc
FANN_SITE = git://github.com/libfann/fann.git
FANN_LICENSE = GNU Lesser General Public License v2.1
FANN_AUTORECONF = YES
FANN_INSTALL_STAGING = YES
FANN_DEPENDENCIES = host-pkgconf host-automake host-autoconf host-libtool

$(eval $(cmake-package))
$(eval $(host-cmake-package))
