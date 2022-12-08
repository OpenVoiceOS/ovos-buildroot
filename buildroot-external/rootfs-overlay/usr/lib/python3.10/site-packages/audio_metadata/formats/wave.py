# http://soundfile.sapp.org/doc/WaveFormat/
# http://www-mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/WAVE.html

__all__ = [
	'RIFFTag',
	'RIFFTags',
	'WAVE',
	'WAVEStreamInfo',
	'WAVESubchunk',
]

import os
import struct

from attr import (
	attrib,
	attrs,
)
from bidict import frozenbidict
from tbm_utils import (
	AttrMapping,
	datareader,
)

from .id3v2 import ID3v2
from .tables import WAVEAudioFormat
from ..exceptions import FormatError
from ..models import (
	Format,
	StreamInfo,
	Tag,
	Tags,
)


class RIFFTag(Tag):
	@datareader
	@classmethod
	def parse(cls, data):
		name = data.read(4).decode('utf-8')
		size = struct.unpack('I', data.read(4))[0]
		value = data.read(size).strip(b'\x00').decode('utf-8')

		return cls(
			name=name,
			value=value,
		)


# https://www.recordingblogs.com/wiki/list-chunk-of-a-wave-file
class RIFFTags(Tags):
	FIELD_MAP = frozenbidict(
		{
			'album': 'IPRD',
			'artist': 'IART',
			'comment': 'ICMT',
			'copyright': 'ICOP',
			'date': 'ICRD',
			'encodedby': 'IENC',
			'genre': 'IGNR',
			'language': 'ILNG',
			'rating': 'IRTD',
			'title': 'INAM',
			'tracknumber': 'ITRK',
		},
	)

	@datareader
	@classmethod
	def parse(cls, data):
		if data.read(4) != b'INFO':
			raise FormatError("Valid RIFF INFO chunk not found.")

		fields = {}

		name = data.peek(4)
		while len(name):
			field = RIFFTag.parse(data)
			fields[field.name] = [field.value]

			b = data.read(1)
			while b == b'\x00':
				b = data.read(1)

			if b:
				data.seek(-1, os.SEEK_CUR)

			name = data.peek(4)

		return cls(fields)


@attrs(
	repr=False,
	kw_only=True,
)
class WAVESubchunk(AttrMapping):
	id = attrib()  # noqa
	data = attrib()


@attrs(
	repr=False,
	kw_only=True,
)
class WAVEStreamInfo(StreamInfo):
	_start = attrib()
	_size = attrib()
	_extension_data = attrib()
	audio_format = attrib(converter=WAVEAudioFormat)
	bit_depth = attrib()
	bitrate = attrib()
	channels = attrib()
	duration = attrib()
	sample_rate = attrib()

	@datareader
	@classmethod
	def parse(cls, data):
		audio_format, channels, sample_rate = struct.unpack(
			'HHI',
			data.read(8),
		)

		byte_rate, block_align, bit_depth = struct.unpack(
			'<IHH',
			data.read(8),
		)

		bitrate = byte_rate * 8

		return cls(
			start=None,
			size=None,
			extension_data=None,
			audio_format=WAVEAudioFormat(audio_format),
			bit_depth=bit_depth,
			bitrate=bitrate,
			channels=channels,
			duration=None,
			sample_rate=sample_rate,
		)


class WAVE(Format):
	"""WAVE file format object.

	Extends `Format`.

	Attributes:
		pictures (list): A list of :class:`ID3v2Picture` objects.
		streaminfo (WAVStreamInfo): The audio stream information.
		tags (ID3v2Frames or RIFFTags): The ID3v2 or RIFF tags, if present.
	"""

	tags_type = RIFFTags

	def __init__(self):
		super().__init__()
		self._subchunks = []

	@datareader
	@staticmethod
	def _parse_subchunk(data):
		subchunk_id, subchunk_size = struct.unpack(
			'4sI',
			data.read(8),
		)

		if subchunk_id == b'fmt ':
			subchunk = WAVEStreamInfo.parse(data)
			if subchunk_size > 16:
				subchunk._extension_data = data.read(subchunk_size - 16)  # Add raw extension data if not PCM.
		elif (
			subchunk_id == b'LIST'
			and data.peek(4) == b'INFO'
		):
			subchunk = RIFFTags.parse(data.read(subchunk_size))
		elif subchunk_id.lower() == b'id3 ':
			try:
				subchunk = ID3v2.parse(data)
			except FormatError:
				raise
		else:
			subchunk = WAVESubchunk(
				id=subchunk_id,
				data=data.read(subchunk_size),
			)

		return subchunk

	@classmethod
	def parse(cls, data):
		self = super()._load(data)

		chunk_id = self._obj.read(4)

		# chunk_size
		self._obj.read(4)

		format_ = self._obj.read(4)

		if chunk_id != b'RIFF' or format_ != b'WAVE':
			raise FormatError("Valid WAVE header not found.")

		subchunk_header = self._obj.peek(8)
		while len(subchunk_header) == 8:
			subchunk = self._parse_subchunk(self._obj)

			if (
				isinstance(subchunk, WAVESubchunk)
				and subchunk.id == b'data'
			):
				audio_size = len(subchunk.data)
				audio_start = self._obj.tell() - audio_size
			elif isinstance(subchunk, WAVEStreamInfo):
				self.streaminfo = subchunk
			elif isinstance(subchunk, RIFFTags):
				self._riff = subchunk
			elif isinstance(subchunk, ID3v2):
				self._id3 = subchunk
			else:
				self._subchunks.append(subchunk)

			subchunk_header = self._obj.peek(8)

		try:
			self.streaminfo._start = audio_start
			self.streaminfo._size = audio_size
			self.streaminfo.duration = self.streaminfo._size / (self.streaminfo.bitrate / 8)
		except UnboundLocalError:
			raise FormatError("Valid WAVE stream info not found.") from None

		if '_id3' in self:
			self.pictures = self._id3.pictures
			self.tags = self._id3.tags
		elif '_riff' in self:
			self.tags = self._riff

		self._obj.close()

		return self
