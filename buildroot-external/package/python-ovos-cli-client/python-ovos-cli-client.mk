################################################################################
#
# python-ovos-cli-client
#
################################################################################

PYTHON_OVOS_CLI_CLIENT_VERSION = 71677be6c32094e1c719f4f7bc4e849806c38d61
PYTHON_OVOS_CLI_CLIENT_SITE = $(call github,OpenVoiceOS,ovos_cli_client,$(PYTHON_OVOS_CLI_CLIENT_VERSION))
PYTHON_OVOS_CLI_CLIENT_SETUP_TYPE = setuptools
PYTHON_OVOS_CLI_CLIENT_LICENSE_FILES = LICENSE

$(eval $(python-package))
