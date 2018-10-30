################################################################################
#
# fann
#
################################################################################

FANN_VERSION = b211dc3db3a6a2540a34fbe8995bf2df63fc9939
FANN_SITE = git://github.com/libfann/fann.git
FANN_LICENSE = GNU Lesser General Public License v2.1
FANN_AUTORECONF = YES
FANN_INSTALL_STAGING = YES
FANN_DEPENDENCIES = host-pkgconf host-automake host-autoconf host-libtool

$(eval $(cmake-package))
$(eval $(host-cmake-package))
