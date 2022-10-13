################################################################################
#
# python-ovos-cli-client
#
################################################################################

PYTHON_OVOS_CLI_CLIENT_VERSION = 49b01bdff4e9daac69104ce9cbc3184544515953
PYTHON_OVOS_CLI_CLIENT_SITE = $(call github,OpenVoiceOS,ovos_cli_client,$(PYTHON_OVOS_CLI_CLIENT_VERSION))
PYTHON_OVOS_CLI_CLIENT_SETUP_TYPE = setuptools
PYTHON_OVOS_CLI_CLIENT_LICENSE_FILES = LICENSE

$(eval $(python-package))
