################################################################################
#
# python-ovos-cli-client
#
################################################################################

PYTHON_OVOS_CLI_CLIENT_VERSION = e7c1b5c6b471822a237d6367c4b1b4d3fcf284a7
PYTHON_OVOS_CLI_CLIENT_SITE = $(call github,OpenVoiceOS,ovos_cli_client,$(PYTHON_OVOS_CLI_CLIENT_VERSION))
PYTHON_OVOS_CLI_CLIENT_SETUP_TYPE = setuptools
PYTHON_OVOS_CLI_CLIENT_LICENSE_FILES = LICENSE

$(eval $(python-package))
