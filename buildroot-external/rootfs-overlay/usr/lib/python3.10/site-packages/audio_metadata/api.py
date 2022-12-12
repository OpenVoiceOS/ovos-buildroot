__all__ = [
	'determine_format',
	'load',
	'loads',
]

import os
from io import (
	BufferedReader,
	FileIO,
)

from tbm_utils import DataReader

from .exceptions import (
	FormatError,
	UnsupportedFormat,
)
from .formats import (
	FLAC,
	MP3,
	WAVE,
	ID3v2,
	MP3StreamInfo,
	OggOpus,
	OggVorbis,
)


def determine_format(data):
	"""Determine the format of a filepath, file-like object, or bytes-like object.

	Parameters:
		data (bytes-like object, str, os.PathLike, or file-like object):
			A bytes-like object, filepath, path-like object
			or file-like object of an audio file.

	Returns:
		Format: An appropriate audio format class if supported, else None.
	"""

	# Only convert if not already a DataReader.
	# Otherwise ``find_mpeg_frames`` caching won't work.
	if not isinstance(data, DataReader):
		try:
			data = DataReader(data)
		except AttributeError:
			return None

	data.seek(0, os.SEEK_SET)
	d = data.peek(36)

	if (
		d.startswith(b'OggS')
		and b'OpusHead' in d
	):
		return OggOpus

	if (
		d.startswith(b'OggS')
		and b'\x01vorbis' in d
	):
		return OggVorbis

	if d.startswith(b'fLaC'):
		return FLAC

	if d.startswith(b'RIFF'):
		return WAVE

	if d.startswith(b'ID3'):
		ID3v2.parse(data)

	if data.peek(4) == b'fLaC':
		return FLAC

	try:
		MP3StreamInfo.find_mpeg_frames(data)
	except FormatError:
		return None
	else:
		return MP3


def load(f):
	"""Load audio metadata from a filepath or file-like object.

	Parameters:
		f (str, os.PathLike, or file-like object):
			A filepath, path-like object or file-like object of an audio file.

	Returns:
		Format: An audio format object of the appropriate type.

	Raises:
		FormatError: If the audio file is not valid.
		UnsupportedFormat: If the audio file is not of a supported format.
		ValueError: If ``f`` is not a valid str, path-like object,
			file-like object, or is unreadable.
	"""

	if (
		not isinstance(f, (os.PathLike, str))
		and not (
			isinstance(f, BufferedReader)
			and isinstance(f.raw, FileIO)
		)
	):
		raise ValueError("Not a valid filepath or file-like object.")

	data = DataReader(f)

	parser_cls = determine_format(data)

	if parser_cls is None:
		raise UnsupportedFormat("Supported format signature not found.")
	else:
		data.seek(0, os.SEEK_SET)

	return parser_cls.parse(data)


def loads(b):
	"""Load audio metadata from a bytes-like object.

	Parameters:
		b (bytes-like object): A bytes-like object of an audio file.

	Returns:
		Format: An audio format object of the appropriate type.

	Raises:
		FormatError: If the audio file is not valid.
		UnsupportedFormat: If the audio file is not of a supported format.
		ValueError: If ``b`` is not a valid bytes-like object.
	"""

	try:
		memoryview(b)
	except TypeError:
		raise ValueError("Not a valid bytes-like object.")

	data = DataReader(b)

	parser_cls = determine_format(data)

	if parser_cls is None:
		raise UnsupportedFormat("Supported format signature not found.")
	else:
		data.seek(0, os.SEEK_SET)

	return parser_cls.parse(data)
