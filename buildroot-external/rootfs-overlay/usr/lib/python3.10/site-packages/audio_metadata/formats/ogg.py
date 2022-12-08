# https://xiph.org/ogg/doc/
# https://wiki.xiph.org/Ogg
# https://helpful.knobs-dials.com/index.php/Ogg_notes

__all__ = [
	'Ogg',
	'OggPage',
	'OggPageHeader',
	'OggPageSegments',
]

import os
import struct

import bitstruct
from attr import (
	attrib,
	attrs,
)
from tbm_utils import (
	AttrMapping,
	LabelList,
	datareader,
)

from ..exceptions import (
	FormatError,
	UnsupportedFormat,
)
from ..models import Format


@attrs(
	repr=False,
	kw_only=True,
)
class OggPageHeader(AttrMapping):
	_start = attrib()
	version = attrib()
	is_continued = attrib(converter=bool)
	is_first = attrib(converter=bool)
	is_last = attrib(converter=bool)
	position = attrib()
	serial_number = attrib()
	sequence_number = attrib()
	crc = attrib()
	num_segments = attrib()

	@datareader
	@classmethod
	def parse(cls, data):
		start = data.tell()

		(
			oggs, version, flags,
			position, serial_number,
			sequence_number, crc, num_segments
		) = struct.unpack(
			'<4sBsqIIIB',
			data.read(27),
		)

		if oggs != b'OggS':
			raise FormatError("Valid Ogg page header not found.")

		if version != 0:
			raise UnsupportedFormat(f"Ogg version '{version}' is not supported.")

		is_last, is_first, is_continued = bitstruct.unpack('<p5 b1 b1 b1', flags)

		return cls(
			start=start,
			version=version,
			is_continued=is_continued,
			is_first=is_first,
			is_last=is_last,
			position=position,
			serial_number=serial_number,
			sequence_number=sequence_number,
			crc=crc,
			num_segments=num_segments,
		)


class OggPageSegments(LabelList):
	item_label = ('segment', 'segments')


@attrs(
	repr=False,
	kw_only=True,
)
class OggPage(AttrMapping):
	_header = attrib()
	is_complete = attrib()
	is_continued = attrib(converter=bool)
	is_first = attrib(converter=bool)
	is_last = attrib(converter=bool)
	position = attrib()
	serial_number = attrib()
	sequence_number = attrib()
	crc = attrib()
	num_segments = attrib()
	segments = attrib(converter=OggPageSegments)

	@datareader
	@classmethod
	def parse(cls, data):
		header = OggPageHeader.parse(data)

		segment_sizes = []
		total = 0
		for segment in data.read(header.num_segments):
			total += segment
			if segment < 255:
				segment_sizes.append(total)
				total = 0

		is_complete = True
		if total:
			segment_sizes.append(total)
			is_complete = False

		segments = [
			data.read(segment_size)
			for segment_size in segment_sizes
		]

		return cls(
			header=header,
			is_complete=is_complete,
			is_continued=header.is_continued,
			is_first=header.is_first,
			is_last=header.is_last,
			position=header.position,
			serial_number=header.serial_number,
			sequence_number=header.sequence_number,
			crc=header.crc,
			num_segments=header.num_segments,
			segments=segments,
		)


class Ogg(Format):
	"""Ogg file format object.

	Extends `Format`.

	Base class for various formats using an Ogg container.
	"""

	def find_last_page(self, info_serial):
		self._obj.seek(0, os.SEEK_END)
		size = self._obj.tell()

		if size > 65536:
			self._obj.seek(-65536, os.SEEK_END)
		else:
			self._obj.seek(0, os.SEEK_SET)

		data = self._obj.read()
		try:
			index = data.rindex(b'OggS')
		except ValueError:
			raise Exception  # TODO

		self._obj.seek(-(len(data) - index), os.SEEK_END)

		last_page = None
		try:
			page = OggPage.parse(self._obj)
		except Exception:  # TODO
			pass
		else:
			if (
				page.serial_number == info_serial
				and (
					not page.is_continued
					or page.position != -1
				)
			):
				if page.is_last:
					last_page = page

		if last_page is None:
			self._obj.seek(0, os.SEEK_SET)
			try:
				page = OggPage.parse(self._obj)
				while True:
					if page.serial_number == info_serial:
						if (
							not page.is_continued
							or page.position != -1
						):
							last_page = page

							if page.is_last:
								break

					page = OggPage.parse(self._obj)
			except Exception:
				pass

		return last_page

	def parse_pages(self):
		while (self.filesize - self._obj.tell()) >= 27:
			yield OggPage.parse(self._obj)
