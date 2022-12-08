__all__ = [
	'Namespace',
	'SubcommandHelpFormatter',
	'UsageHelpFormatter',
	'create_parser_dry_run',
	'create_parser_filter_dates',
	'create_parser_local',
	'create_parser_logging',
	'create_parser_meta',
	'create_parser_yes',
	'custom_path',
	'merge_defaults',
	'parse_args'
]

import argparse
import os
from pathlib import Path

from .datetime import datetime_string_to_time_period
from .path import UNIX_PATH_RE, convert_unix_path
from .structures import AttrMapping


#########
# Utils #
#########

# I use Windows Python install from Cygwin.
# This converts Unix-style paths to Windows-style paths.
def custom_path(value):
	if os.name == 'nt' and UNIX_PATH_RE.match(str(value)):
		value = Path(convert_unix_path(str(value)))

	value = Path(value)

	return value


###########
# Parsers #
###########

def create_parser_meta(title, version):
	meta = argparse.ArgumentParser(
		add_help=False
	)

	meta_options = meta.add_argument_group("Options")
	meta_options.add_argument(
		'-h', '--help',
		action='help',
		help="Display help."
	)
	meta_options.add_argument(
		'-V', '--version',
		action='version',
		version=f"{title} {version}",
		help="Output version."
	)

	return meta


def create_parser_dry_run():
	dry_run = argparse.ArgumentParser(
		argument_default=argparse.SUPPRESS,
		add_help=False
	)

	dry_run_options = dry_run.add_argument_group("Action")
	dry_run_options.add_argument(
		'-n', '--dry-run',
		action='store_true',
		help="Output results without taking action."
	)

	return dry_run


def create_parser_yes():
	yes = argparse.ArgumentParser(
		argument_default=argparse.SUPPRESS,
		add_help=False
	)

	yes_options = yes.add_argument_group("Action")
	yes_options.add_argument(
		'-y', '--yes',
		action='store_true',
		help="Don't ask for confirmation."
	)

	return yes


def create_parser_logging():
	logging_ = argparse.ArgumentParser(
		argument_default=argparse.SUPPRESS,
		add_help=False
	)

	logging_options = logging_.add_argument_group("Logging")
	logging_options.add_argument(
		'-v', '--verbose',
		action='count',
		help="Increase verbosity of output."
	)
	logging_options.add_argument(
		'-q', '--quiet',
		action='count',
		help="Decrease verbosity of output."
	)
	logging_options.add_argument(
		'--debug',
		action='store_true',
		help="Output log messages from dependencies."
	)
	logging_options.add_argument(
		'--log-to-stdout',
		action='store_true',
		help="Log to stdout."
	)
	logging_options.add_argument(
		'--no-log-to-stdout',
		action='store_true',
		help="Don't log to stdout."
	)
	logging_options.add_argument(
		'--log-to-file',
		action='store_true',
		help="Log to file."
	)
	logging_options.add_argument(
		'--no-log-to-file',
		action='store_true',
		help="Don't log to file."
	)

	return logging_


def create_parser_local():
	local = argparse.ArgumentParser(
		argument_default=argparse.SUPPRESS,
		add_help=False
	)

	local_options = local.add_argument_group("Local")
	local_options.add_argument(
		'--no-recursion',
		action='store_true',
		help=(
			"Disable recursion when scanning for local files.\n"
			"Recursion is enabled by default."
		)
	)
	local_options.add_argument(
		'--max-depth',
		metavar='DEPTH',
		type=int,
		help=(
			"Set maximum depth of recursion when scanning for local files.\n"
			"Default is infinite recursion."
		)
	)
	local_options.add_argument(
		'-xp', '--exclude-path',
		metavar='PATH',
		action='append',
		dest='exclude_paths',
		help=(
			"Exclude filepaths.\n"
			"Can be specified multiple times."
		)
	)
	local_options.add_argument(
		'-xr', '--exclude-regex',
		metavar='RX',
		action='append',
		dest='exclude_regexes',
		help=(
			"Exclude filepaths using regular expressions.\n"
			"Can be specified multiple times."
		)
	)
	local_options.add_argument(
		'-xg', '--exclude-glob',
		metavar='GP',
		action='append',
		dest='exclude_globs',
		help=(
			"Exclude filepaths using glob patterns.\n"
			"Can be specified multiple times.\n"
			"Absolute glob patterns not supported."
		)
	)

	return local


def create_parser_filter_dates():
	filter_dates = argparse.ArgumentParser(
		argument_default=argparse.SUPPRESS,
		add_help=False
	)

	dates_options = filter_dates.add_argument_group("Filter")
	dates_options.add_argument(
		'--created-in',
		metavar='DATE',
		type=lambda d: datetime_string_to_time_period(d, in_=True),
		help="Include items created in year or year/month."
	)
	dates_options.add_argument(
		'--created-on',
		metavar='DATE',
		type=lambda d: datetime_string_to_time_period(d, on=True),
		help="Include items created on date."
	)
	dates_options.add_argument(
		'--created-before',
		metavar='DATE',
		type=lambda d: datetime_string_to_time_period(d, before=True),
		help="Include items created before datetime."
	)
	dates_options.add_argument(
		'--created-after',
		metavar='DATE',
		type=lambda d: datetime_string_to_time_period(d, after=True),
		help="Include items created after datetime."
	)
	dates_options.add_argument(
		'--modified-in',
		metavar='DATE',
		type=lambda d: datetime_string_to_time_period(d, in_=True),
		help="Include items created in year or year/month."
	)
	dates_options.add_argument(
		'--modified-on',
		metavar='DATE',
		type=lambda d: datetime_string_to_time_period(d, on=True),
		help="Include items created on date."
	)
	dates_options.add_argument(
		'--modified-before',
		metavar='DATE',
		type=lambda d: datetime_string_to_time_period(d, before=True),
		help="Include items modified before datetime."
	)
	dates_options.add_argument(
		'--modified-after',
		metavar='DATE',
		type=lambda d: datetime_string_to_time_period(d, after=True),
		help="Include items modified after datetime."
	)

	return filter_dates


############
# argparse #
############

class Namespace(AttrMapping):
	pass


class UsageHelpFormatter(argparse.RawTextHelpFormatter):  # pragma: nocover
	def add_usage(self, usage, actions, groups, prefix="Usage: "):
		super().add_usage(usage, actions, groups, prefix)


# Removes the command list while leaving the usage metavar intact.
class SubcommandHelpFormatter(UsageHelpFormatter):  # pragma: nocover
	def _format_action(self, action):
		parts = super()._format_action(action)
		if action.nargs == argparse.PARSER:
			parts = "\n".join(parts.split("\n")[1:])
		return parts


def merge_defaults(defaults, parsed):
	args = Namespace()

	args.update(defaults)
	args.update(parsed)

	return args


def parse_args(parser, args=None):
	return parser.parse_args(args, namespace=Namespace())
