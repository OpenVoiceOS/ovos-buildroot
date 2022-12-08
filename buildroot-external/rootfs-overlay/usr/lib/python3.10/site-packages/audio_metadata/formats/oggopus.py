__all__ = [
	'OggOpus',
	'OggOpusStreamInfo',
	'OggOpusVorbisComments',
]

import os
import struct
from base64 import b64decode

from attr import (
	attrib,
	attrs,
)
from tbm_utils import datareader

from .flac import FLACPicture
from .ogg import Ogg
from .vorbiscomments import VorbisComments
from ..exceptions import FormatError
from ..models import StreamInfo


class OggOpusVorbisComments(VorbisComments):
	@datareader
	@classmethod
	def parse(cls, data):
		if data.read(8) != b'OpusTags':
			raise Exception  # TODO

		return super().parse(data)


@attrs(
	repr=False,
	kw_only=True,
)
class OggOpusStreamInfo(StreamInfo):
	_start = attrib()
	_size = attrib()
	_version = attrib()
	bitrate = attrib()
	channel_map = attrib()  # TODO
	channels = attrib()
	duration = attrib()
	output_gain = attrib()
	pre_skip = attrib()
	sample_rate = attrib(default=48000)
	source_sample_rate = attrib()

	@datareader
	@classmethod
	def parse(cls, data):
		if data.read(8) != b'OpusHead':
			raise Exception  # TODO

		(
			version, channels, pre_skip,
			source_sample_rate, output_gain, channel_map
		) = struct.unpack(
			'<BBHIhB',
			data.read(11),
		)

		if version >> 4:
			raise Exception  # TODO

		return cls(
			start=None,
			size=None,
			version=version,
			bitrate=None,
			channel_map=channel_map,
			channels=channels,
			duration=None,
			output_gain=output_gain,
			pre_skip=pre_skip,
			source_sample_rate=source_sample_rate,
		)


class OggOpus(Ogg):
	"""Ogg Opus file format object.

	Extends `Format`.

	Attributes:
		pictures (list): A list of `FLACPicture` objects.
		streaminfo (OggOpusStreamInfo): The audio stream information.
		tags (OggOpusVorbisComments): The Vorbis comment metadata block.
	"""

	tags_type = OggOpusVorbisComments

	@classmethod
	def parse(cls, data):
		self = super()._load(data)

		self._obj.seek(0, os.SEEK_SET)
		if self._obj.peek(4) != b'OggS':
			raise FormatError("Valid Ogg page header not found.")

		page = next(self.parse_pages())

		if not page.segments[0].startswith(b'OpusHead'):
			raise FormatError(f"``OpusHead`` must be first page in Ogg Opus.")
		else:
			self.streaminfo = OggOpusStreamInfo.parse(page.segments[0])
			info_serial = page.serial_number

		audio_start = self._obj.tell()

		page = next(self.parse_pages())
		if (
			page.serial_number == info_serial
			and page.segments[0].startswith(b'OpusTags')
		):
			audio_start = self._obj.tell()

			tag_pages = [page]
			while not (
				tag_pages[-1].is_complete
				or len(tag_pages[-1].segments) > 1
			):
				page = next(self.parse_pages())
				if page.serial_number == tag_pages[0].serial_number:
					tag_pages.append(page)

					audio_start = self._obj.tell()

		last_page = self.find_last_page(info_serial)
		audio_end = self._obj.tell()

		self.streaminfo._start = audio_start
		self.streaminfo._size = audio_end - audio_start
		self.streaminfo.duration = (last_page.position - self.streaminfo.pre_skip) / 48000
		self.streaminfo.bitrate = (self.streaminfo._size * 8) / self.streaminfo.duration

		tag_data = b''.join(
			page.segments[0]
			for page in tag_pages
		)
		self.tags = OggOpusVorbisComments.parse(tag_data)

		pictures = self.tags.pop('metadata_block_picture', [])
		self.pictures = [
			FLACPicture.parse(b64decode(picture))
			for picture in pictures
		]

		self._obj.close()

		return self
