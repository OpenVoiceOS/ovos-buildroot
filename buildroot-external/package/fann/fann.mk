################################################################################
#
# fann
#
################################################################################

FANN_VERSION = 7ec1fc7e5bd734f1d3c89b095e630e83c86b9be1
FANN_SITE = git://github.com/libfann/fann.git
FANN_LICENSE = GNU Lesser General Public License v2.1
FANN_AUTORECONF = YES
FANN_INSTALL_STAGING = YES
FANN_DEPENDENCIES = host-pkgconf host-automake host-autoconf host-libtool

$(eval $(cmake-package))
$(eval $(host-cmake-package))
