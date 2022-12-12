# https://xiph.org/vorbis/doc/Vorbis_I_spec.html
# https://xiph.org/vorbis/doc/v-comment.html

__all__ = [
	'OggVorbis',
	'OggVorbisComments',
	'OggVorbisStreamInfo',
]

import os
import struct
from base64 import b64decode

import bitstruct
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


class OggVorbisComments(VorbisComments):
	@datareader
	@classmethod
	def parse(cls, data):
		if data.read(7) != b'\x03vorbis':
			raise Exception  # TODO

		comments = super().parse(data)

		if bitstruct.unpack('p7 b1', data.read(1))[0] is False:
			raise FormatError("Ogg Vorbis comments framing bit unset.")

		return comments


# TODO: Bitrate mode based
@attrs(
	repr=False,
	kw_only=True,
)
class OggVorbisStreamInfo(StreamInfo):
	_start = attrib()
	_size = attrib()
	_version = attrib()
	bitrate = attrib()
	channels = attrib()
	duration = attrib()
	max_bitrate = attrib()
	min_bitrate = attrib()
	nominal_bitrate = attrib()
	sample_rate = attrib()

	@datareader
	@classmethod
	def parse(cls, data):
		if data.read(7) != b'\x01vorbis':
			raise Exception  # TODO

		version = struct.unpack('<I', data.read(4))

		(
			channels, sample_rate, max_bitrate,
			nominal_bitrate, min_bitrate
		) = struct.unpack(
			'<B4i',
			data.read(17),
		)

		return cls(
			start=None,
			size=None,
			version=version,
			bitrate=None,
			channels=channels,
			duration=None,
			max_bitrate=max_bitrate,
			min_bitrate=min_bitrate,
			nominal_bitrate=nominal_bitrate,
			sample_rate=sample_rate,
		)


class OggVorbis(Ogg):
	"""Ogg Vorbis file format object.

	Extends `Format`.

	Attributes:
		pictures (list): A list of `FLACPicture` objects.
		streaminfo (OggVorbisStreamInfo): The audio stream information.
		tags (OggVorbisComments): The Vorbis comment metadata block.
	"""

	tags_type = OggVorbisComments

	@classmethod
	def parse(cls, data):
		self = super()._load(data)

		self._obj.seek(0, os.SEEK_SET)
		if self._obj.peek(4) != b'OggS':
			raise FormatError("Valid Ogg page header not found.")

		page = next(self.parse_pages())

		if not page.segments[0].startswith(b'\x01vorbis'):
			raise FormatError(f"``\x01vorbis`` must be first page in Ogg Vorbis.")
		else:
			self.streaminfo = OggVorbisStreamInfo.parse(page.segments[0])
			info_serial = page.serial_number

		audio_start = self._obj.tell()

		page = next(self.parse_pages())
		if (
			page.serial_number == info_serial
			and page.segments[0].startswith(b'\x03vorbis')
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
		self.streaminfo.duration = last_page.position / self.streaminfo.sample_rate
		self.streaminfo.bitrate = (self.streaminfo._size * 8) / self.streaminfo.duration

		tag_data = b''.join(
			page.segments[0]
			for page in tag_pages
		)
		self.tags = OggVorbisComments.parse(tag_data)

		pictures = self.tags.pop('metadata_block_picture', [])
		self.pictures = [
			FLACPicture.parse(b64decode(picture))
			for picture in pictures
		]

		self._obj.close()

		return self
