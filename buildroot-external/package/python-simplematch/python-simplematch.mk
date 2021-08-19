################################################################################
#
# python-simplematch
#
################################################################################

PYTHON_SIMPLEMATCH_VERSION = 1.3
PYTHON_SIMPLEMATCH_SOURCE = simplematch-$(PYTHON_SIMPLEMATCH_VERSION).tar.gz
PYTHON_SIMPLEMATCH_SITE = https://files.pythonhosted.org/packages/1a/3d/4504e218fe50c988c8229fe4bfd5633ed43e1fa79de7147c5ddfec270fae
PYTHON_SIMPLEMATCH_SETUP_TYPE = setuptools
PYTHON_SIMPLEMATCH_LICENSE = MIT
PYTHON_SIMPLEMATCH_LICENSE_FILES = LICENSE.txt

$(eval $(python-package))
