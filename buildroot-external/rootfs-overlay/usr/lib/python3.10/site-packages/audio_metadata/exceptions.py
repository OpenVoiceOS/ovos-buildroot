__all__ = [
	'AudioMetadataException',
	'AudioMetadataWarning',
	'FormatError',
	'TagError',
	'UnsupportedFormat',
]

import sys
import warnings


##############
# Exceptions #
##############

class AudioMetadataException(Exception):
	"""Base exception for audio-metadata."""


class UnsupportedFormat(AudioMetadataException):
	"""An unsupported format, version, or profile was encountered."""


class FormatError(AudioMetadataException):
	"""The binary format of a data input is invalid."""


class TagError(AudioMetadataException):
	"""A tag is not compliant to a specification."""


############
# Warnings #
############

# Override warning output format.
def showwarning(message, category, filename, lineno, file=None, line=None):  # pragma: nocover
	if file is None:
		file = sys.stderr
		if file is None:
			return

	delim = '\n    '
	nl = '\n'
	s = f"{category.__name__}:{delim}{delim.join(line for line in str(message).split(nl))}\n"

	try:
		file.write(s)
	except (IOError, UnicodeError):
		pass


warnings.showwarning = showwarning
del showwarning


class AudioMetadataWarning(UserWarning):
	"""Base warning for audio-metadata."""


warnings.simplefilter(
	'always',
	category=AudioMetadataWarning,
)
