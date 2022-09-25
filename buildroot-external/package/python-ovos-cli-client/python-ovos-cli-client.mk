################################################################################
#
# python-ovos-cli-client
#
################################################################################

PYTHON_OVOS_CLI_CLIENT_VERSION = d496123552814b3f4764b6005f5e76dbc82f72e3
PYTHON_OVOS_CLI_CLIENT_SITE = $(call github,OpenVoiceOS,ovos_cli_client,$(PYTHON_OVOS_CLI_CLIENT_VERSION))
PYTHON_OVOS_CLI_CLIENT_SETUP_TYPE = setuptools
PYTHON_OVOS_CLI_CLIENT_LICENSE_FILES = LICENSE

$(eval $(python-package))
