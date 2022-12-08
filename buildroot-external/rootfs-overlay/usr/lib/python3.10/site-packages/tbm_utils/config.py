__all__ = [
	'convert_default_keys',
	'get_defaults'
]

from collections.abc import Mapping

from .structures import AttrMapping


def convert_default_keys(item):
	if isinstance(item, Mapping):
		converted = item.__class__()
		for k, v in item.items():
			converted[k.lstrip('-').replace('-', '_')] = convert_default_keys(v)

		return converted
	else:
		return item


def get_defaults(command, config, *, command_keys=None, command_aliases=None):
	config_defaults = config.get('defaults')
	defaults = AttrMapping()

	if config_defaults:
		command_keys = command_keys or set()

		defaults.update(
			(k, v)
			for k, v in config_defaults.items()
			if k not in command_keys
		)

		if command in config_defaults:
			defaults.update(
				(k, v)
				for k, v in config_defaults[command].items()
				if k not in command_keys
			)

		if command_aliases is not None:
			cmd_alias = command_aliases.get(command)
			if cmd_alias and cmd_alias in config_defaults:
				defaults.update(
					(k, v)
					for k, v in config_defaults[cmd_alias].items()
					if k not in command_keys
				)

	return convert_default_keys(defaults)
