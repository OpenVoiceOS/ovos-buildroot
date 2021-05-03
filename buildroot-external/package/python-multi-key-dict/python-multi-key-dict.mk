################################################################################
#
# python-multi-key-dict
#
################################################################################

PYTHON_MULTI_KEY_DICT_VERSION = 2.0.3
PYTHON_MULTI_KEY_DICT_SOURCE = multi_key_dict-$(PYTHON_MULTI_KEY_DICT_VERSION).tar.gz
PYTHON_MULTI_KEY_DICT_SITE = https://files.pythonhosted.org/packages/6d/97/2e9c47ca1bbde6f09cb18feb887d5102e8eacd82fbc397c77b221f27a2ab
PYTHON_MULTI_KEY_DICT_SETUP_TYPE = distutils
PYTHON_MULTI_KEY_DICT_LICENSE = MIT

$(eval $(python-package))
