# https://xiph.org/flac/format.html

__all__ = [
	'FLAC',
	'FLACApplication',
	'FLACCueSheet',
	'FLACCueSheetIndex',
	'FLACCueSheetTrack',
	'FLACMetadataBlock',
	'FLACPadding',
	'FLACPicture',
	'FLACSeekPoint',
	'FLACSeekTable',
	'FLACStreamInfo',
	'FLACVorbisComments',
]

import binascii
import struct

from attr import (
	Factory,
	attrib,
	attrs,
)
from tbm_utils import (
	AttrMapping,
	LabelList,
	datareader,
)

from .id3v2 import ID3v2
from .tables import (
	FLACMetadataBlockType,
	ID3PictureType,
)
from .vorbiscomments import VorbisComments
from ..exceptions import FormatError
from ..models import (
	Format,
	Picture,
	StreamInfo,
)

try:
	import bitstruct.c as bitstruct
except ImportError:
	import bitstruct


@attrs(
	repr=False,
	kw_only=True,
)
class FLACApplication(AttrMapping):
	"""A FLAC application metadata block.

	Attributes:
		id (str): The 32-bit application identifier.
		data (bytes): The data defined by the application.
	"""

	id = attrib()  # noqa
	data = attrib()

	def __repr__(self):
		return f"<FLACApplication ({self.id})>"

	@datareader
	@classmethod
	def parse(cls, data):
		id_ = data.read(4).decode('utf-8', 'replace')
		data = data.read()

		return cls(
			id=id_,
			data=data,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class FLACCueSheetIndex(AttrMapping):
	"""A FLAC cue sheet track index point.

	Attributes:
		number (int): The index point number.

			The first index in a track must have a number of 0 or 1.

			Index numbers must increase by 1 and be unique within a track.

			For CD-DA, an index number of 0 corresponds to the track pre-gab.

		offset (int): Offset in samples relative to the track offset.
	"""

	number = attrib()
	offset = attrib()

	@datareader
	@classmethod
	def parse(cls, data):
		offset = struct.unpack(
			'>Q',
			data.read(8),
		)[0]

		number = struct.unpack(
			'>B',
			data.read(1),
		)[0]

		data.read(3)

		return cls(
			number=number,
			offset=offset,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class FLACCueSheetTrack(AttrMapping):
	"""A FLAC cue sheet track.

	Attributes:
		track_number (int): The track number of the track.

			0 is not allowed to avoid conflicting with the CD-DA spec lead-in track.

			For CD-DA, the track number must be 1-99 or 170 for the lead-out track.

			For non-CD-DA, the track number must be 255 for the lead-out track.

			Track numbers must be unique within a cue sheet.
		offset (int): Offset in samples relative to the beginning of the FLAC audio stream.
		isrc (str): The ISRC (International Standard Recording Code) of the track.
		type (int): ``0`` for audio, ``1`` for non-audio.
		pre_emphasis (bool): ``True`` if contains pre-emphasis, ``False`` if not.
		indexes (list): The index points for the track as `FLACCueSheetIndex` objects.
	"""

	track_number = attrib()
	offset = attrib()
	isrc = attrib()
	type = attrib()  # noqa
	pre_emphasis = attrib()
	indexes = attrib(default=Factory(list))

	@datareader
	@classmethod
	def parse(cls, data):
		offset = struct.unpack(
			'>Q',
			data.read(8),
		)[0]
		track_number = struct.unpack(
			'>B',
			data.read(1),
		)[0]
		isrc = data.read(12).rstrip(b'\x00').decode('ascii', 'replace')

		type_, pre_emphasis = bitstruct.unpack(
			'u1 b1',
			data.read(1),
		)

		data.read(13)
		num_indexes = struct.unpack(
			'>B',
			data.read(1),
		)[0]

		indexes = []
		for _ in range(num_indexes):
			indexes.append(FLACCueSheetIndex.parse(data))

		return cls(
			track_number=track_number,
			offset=offset,
			isrc=isrc,
			type=type_,
			pre_emphasis=pre_emphasis,
			indexes=indexes,
		)


class FLACCueSheet(LabelList):
	"""A FLAC cue sheet metadata block.

	A list-like structure of `FLACCueSheetTrack` objects
	along with some information used in the cue sheet.

	Attributes:
		catalog_number (str): The media catalog number.
		lead_in_samples (int): The number of lead-in samples.
			This is only meaningful for CD-DA cuesheets.
			For others, it should be 0.
		compact_disc (bool): ``True`` if the cue sheet corresponds to a compact disc, else ``False``.
	"""

	item_label = ('track', 'tracks')

	def __init__(self, tracks, catalog_number, lead_in_samples, compact_disc):
		super().__init__(tracks)
		self.catalog_number = catalog_number
		self.lead_in_samples = lead_in_samples
		self.compact_disc = compact_disc

	@datareader
	@classmethod
	def parse(cls, data):
		catalog_number = data.read(128).rstrip(b'\0').decode('ascii', 'replace')
		lead_in_samples = struct.unpack(
			'>Q',
			data.read(8),
		)[0]
		compact_disc = bitstruct.unpack(
			'b1',
			data.read(1),
		)[0]

		data.read(258)
		num_tracks = struct.unpack(
			'B',
			data.read(1),
		)[0]

		tracks = []
		for _ in range(num_tracks):
			tracks.append(FLACCueSheetTrack.parse(data))

		return cls(
			tracks,
			catalog_number=catalog_number,
			lead_in_samples=lead_in_samples,
			compact_disc=compact_disc,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class FLACMetadataBlock(AttrMapping):
	"""Generic FLAC metadata block.

	Attributes:
		type (int): Metadata block type index.
		data (bytes): The binary metadata block data.
	"""

	type = attrib()  # noqa
	data = attrib()

	def __repr__(self):
		return f"<FLACMetadataBlock [{self.type}] ({len(self.data)} bytes)>"


@attrs(
	repr=False,
	kw_only=True,
)
class FLACPadding(AttrMapping):
	"""A FLAC padding metadata block.

	Attributes:
		size (int): The size of the padding.
	"""

	size = attrib()

	def __repr__(self):
		return f"<FLACPadding ({self.size} bytes)>"

	@datareader
	@classmethod
	def parse(cls, data):
		return cls(size=len(data.peek()))


class FLACPicture(Picture):
	"""A FLAC picture object.

	Attributes:
		type (ID3PictureType): The picture type according to
			the ID3v2 APIC frame format.
		mime_type (str): The mime type of the picture.
			May indicate that the picture data is an URL
			of the picture instead of picture data.
		description (str): The description of the picture.
		width (int): The width of the picture in pixels.
		height (int): The height of the picture in pixels.
		bit_depth (int): The color depth of the picture
			in bits-per-pixel.
		colors (int): For indexed-color pictures (e.g. GIF),
			the number of colors used.
			Should be 0 for non-indexed-color pictures.
		data (bytes): The binary picture data.
	"""

	@datareader
	@classmethod
	def parse(cls, data):
		type_, mime_length = struct.unpack('>2I', data.read(8))
		mime_type = data.read(mime_length).decode('utf-8', 'replace')

		desc_length = struct.unpack('>I', data.read(4))[0]
		description = data.read(desc_length).decode('utf-8', 'replace')

		width, height, bit_depth, colors = struct.unpack('>4I', data.read(16))

		data_length = struct.unpack('>I', data.read(4))[0]
		data = data.read(data_length)

		return cls(
			type=ID3PictureType(type_),
			mime_type=mime_type,
			description=description,
			width=width,
			height=height,
			bit_depth=bit_depth,
			colors=colors,
			data=data,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class FLACSeekPoint(AttrMapping):
	first_sample = attrib()
	offset = attrib()
	num_samples = attrib()

	@datareader
	@classmethod
	def parse(cls, data):
		first_sample, offset, num_samples = struct.unpack('>QQH', data.read())

		return cls(
			first_sample=first_sample,
			offset=offset,
			num_samples=num_samples,
		)


class FLACSeekTable(LabelList):
	item_label = ('seekpoint', 'seekpoints')

	@datareader
	@classmethod
	def parse(cls, data):
		seekpoints = []
		seekpoint = data.read(18)
		while len(seekpoint) == 18:
			seekpoints.append(FLACSeekPoint.parse(seekpoint))
			seekpoint = data.read(18)

		return cls(seekpoints)


class FLACVorbisComments(VorbisComments):
	@datareader
	@classmethod
	def parse(cls, data):
		return super().parse(data)


@attrs(
	repr=False,
	kw_only=True,
)
class FLACStreamInfo(StreamInfo):
	_start = attrib()
	_size = attrib()
	_min_block_size = attrib()
	_max_block_size = attrib()
	_min_frame_size = attrib()
	_max_frame_size = attrib()
	bit_depth = attrib()
	bitrate = attrib()
	channels = attrib()
	duration = attrib()
	md5 = attrib()
	sample_rate = attrib()

	@datareader
	@classmethod
	def parse(cls, data):
		stream_info_block_data = bitstruct.unpack(
			'u16 u16 u24 u24 u20 u3 u5 u36 r128',
			data.read(34),
		)

		min_block_size = stream_info_block_data[0]
		max_block_size = stream_info_block_data[1]
		min_frame_size = stream_info_block_data[2]
		max_frame_size = stream_info_block_data[3]
		sample_rate = stream_info_block_data[4]
		channels = stream_info_block_data[5] + 1
		bit_depth = stream_info_block_data[6] + 1
		total_samples = stream_info_block_data[7]
		md5sum = binascii.hexlify(stream_info_block_data[8]).decode('ascii', 'replace')
		duration = total_samples / sample_rate

		return cls(
			start=None,
			size=None,
			min_block_size=min_block_size,
			max_block_size=max_block_size,
			min_frame_size=min_frame_size,
			max_frame_size=max_frame_size,
			bit_depth=bit_depth,
			bitrate=None,
			channels=channels,
			duration=duration,
			md5=md5sum,
			sample_rate=sample_rate,
		)


class FLAC(Format):
	"""FLAC file format object.

	Extends `Format`.

	Attributes:
		cuesheet (FLACCueSheet): The cuesheet metadata block.
		pictures (list): A list of `FLACPicture` objects.
		seektable (FLACSeekTable): The seektable metadata block.
		streaminfo (FLACStreamInfo): The audio stream information.
		tags (VorbisComments): The Vorbis comment metadata block.
	"""

	tags_type = VorbisComments

	def __init__(self):
		super().__init__()
		self._blocks = []

	@datareader
	@staticmethod
	def _parse_metadata_block(data):
		is_last_block, block_type, block_size = bitstruct.unpack(
			'b1 u7 u24',
			data.read(4),
		)

		if block_size == 0:
			raise FormatError("FLAC metadata block size must be greater than 0.")

		# There are examples of tools writing incorrect block sizes.
		# The FLAC reference implementation unintentionally (I hope?) parses them.
		# I've chosen not to add special handling for these invalid files.
		# If needed, mutagen (https://github.com/quodlibet/mutagen) may support them.
		metadata_block_data = data.read(block_size)

		if block_type == FLACMetadataBlockType.STREAMINFO:
			metadata_block = FLACStreamInfo.parse(metadata_block_data)
		elif block_type == FLACMetadataBlockType.PADDING:
			metadata_block = FLACPadding.parse(metadata_block_data)
		elif block_type == FLACMetadataBlockType.APPLICATION:
			metadata_block = FLACApplication.parse(metadata_block_data)
		elif block_type == FLACMetadataBlockType.SEEKTABLE:
			metadata_block = FLACSeekTable.parse(metadata_block_data)
		elif block_type == FLACMetadataBlockType.VORBIS_COMMENT:
			metadata_block = FLACVorbisComments.parse(metadata_block_data)
		elif block_type == FLACMetadataBlockType.CUESHEET:
			metadata_block = FLACCueSheet.parse(metadata_block_data)
		elif block_type == FLACMetadataBlockType.PICTURE:
			metadata_block = FLACPicture.parse(metadata_block_data)
		elif block_type >= 127:
			raise FormatError(f"{block_type} is not a valid FLAC metadata block type.")
		else:
			metadata_block = FLACMetadataBlock(
				type=block_type,
				data=metadata_block_data,
			)

		return metadata_block, is_last_block

	@classmethod
	def parse(cls, data):
		self = super()._load(data)

		# Ignore ID3v2 in FLAC.
		if self._obj.peek(3) == b'ID3':
			self._id3 = ID3v2.parse(self._obj)

		if self._obj.read(4) != b'fLaC':
			raise FormatError("Valid FLAC header not found.")

		is_first = True
		while True:
			metadata_block, is_last_block = self._parse_metadata_block(self._obj)

			if (
				is_first
				and not isinstance(metadata_block, FLACStreamInfo)
			):
				raise FormatError("FLAC streaminfo block must be first.")

			is_first = False

			if isinstance(metadata_block, FLACStreamInfo):
				if 'streaminfo' in self:
					raise FormatError("Multiple FLAC streaminfo blocks found.")

				self.streaminfo = metadata_block
			elif isinstance(metadata_block, FLACPadding):
				self.padding = metadata_block
			elif isinstance(metadata_block, FLACApplication):
				self.setdefault('applications', []).append(metadata_block)
			elif isinstance(metadata_block, FLACSeekTable):
				if 'seektable' in self:
					raise FormatError("Multiple FLAC seektable blocks found.")

				self.seektable = metadata_block
			elif isinstance(metadata_block, FLACVorbisComments):
				if self.tags:
					raise FormatError("Multiple FLAC Vorbis comment blocks found.")

				self.tags = metadata_block
			elif isinstance(metadata_block, FLACCueSheet):
				if 'cuesheet' in self:
					raise FormatError("Multiple FLAC cuesheet blocks found.")

				self.cuesheet = metadata_block
			elif isinstance(metadata_block, FLACPicture):
				self.pictures.append(metadata_block)
			else:
				self._blocks.append(metadata_block)

			if is_last_block:
				pos = self._obj.tell()
				self.streaminfo._start = pos
				self.streaminfo._size = self.filesize - self.streaminfo._start

				if self.streaminfo.duration:
					self.streaminfo.bitrate = self.streaminfo._size * 8 / self.streaminfo.duration
				else:
					self.streaminfo.bitrate = 0

				break

		self._obj.close()

		return self
