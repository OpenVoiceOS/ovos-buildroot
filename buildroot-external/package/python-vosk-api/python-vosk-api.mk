################################################################################
#
# python-vosk-api
#
################################################################################

PYTHON_VOSK_API_VERSION = cf2560c9f8a49d3d366b433fdabd78c518231bec
PYTHON_VOSK_API_SITE = $(call github,alphacep,vosk-api,$(PYTHON_VOSK_API_VERSION))
PYTHON_VOSK_API_LICENSE = Apache License 2.0

PYTHON_VOSK_API_DEPENDENCIES = python-cffi python-tqdm python-requests \
				python-srt python-websockets vosk-api
PYTHON_VOSK_API_SUBDIR = python
PYTHON_VOSK_API_SETUP_TYPE = setuptools

PYTHON_VOSK_API_POST_INSTALL_TARGET_HOOKS = PYTHON_VOSK_API_LIBVOSK_SO

define PYTHON_VOSK_API_LIBVOSK_SO
	$(INSTALL) -D -m 755 $(TARGET_DIR)/usr/lib/libvosk.so \
	$(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/vosk/
endef

$(eval $(python-package))
