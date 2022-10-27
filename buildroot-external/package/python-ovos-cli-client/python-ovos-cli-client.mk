################################################################################
#
# python-ovos-cli-client
#
################################################################################

PYTHON_OVOS_CLI_CLIENT_VERSION = 5f6d69372e292010374361ce7e5c2f2388250b47
PYTHON_OVOS_CLI_CLIENT_SITE = $(call github,OpenVoiceOS,ovos_cli_client,$(PYTHON_OVOS_CLI_CLIENT_VERSION))
PYTHON_OVOS_CLI_CLIENT_SETUP_TYPE = setuptools
PYTHON_OVOS_CLI_CLIENT_LICENSE_FILES = LICENSE

$(eval $(python-package))
