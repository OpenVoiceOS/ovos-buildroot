################################################################################
#
# python-webrtcvad
#
################################################################################

PYTHON_WEBRTCVAD_VERSION = e283ca41df3a84b0e87fb1f5cb9b21580a286b09
PYTHON_WEBRTCVAD_SITE = $(call github,wiseman,py-webrtcvad,$(PYTHON_WEBRTCVAD_VERSION))
PYTHON_WEBRTCVAD_SETUP_TYPE = setuptools
PYTHON_WEBRTCVAD_LICENSE = MIT
PYTHON_WEBRTCVAD_LICENSE_FILES = COPYING

$(eval $(python-package))
