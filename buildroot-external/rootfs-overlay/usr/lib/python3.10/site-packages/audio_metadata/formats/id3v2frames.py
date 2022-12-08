# http://id3.org/Developer%20Information

__all__ = [
	'ID3v2APICFrame',
	'ID3v2AudioEncryption',
	'ID3v2AudioEncryptionFrame',
	'ID3v2BinaryDataFrame',
	'ID3v2Comment',
	'ID3v2CommentFrame',
	'ID3v2DateFrame',
	'ID3v2Disc',
	'ID3v2DiscFrame',
	'ID3v2EventTimingCodesFrame',
	'ID3v2Event',
	'ID3v2Events',
	'ID3v2Frame',
	'ID3v2FrameFlags',
	'ID3v2FrameTypes',
	'ID3v2GRIDFrame',
	'ID3v2GeneralEncapsulatedObject',
	'ID3v2GeneralEncapsulatedObjectFrame',
	'ID3v2GenreFrame',
	'ID3v2GroupID',
	'ID3v2InvolvedPeopleListFrame',
	'ID3v2InvolvedPerson',
	'ID3v2Lyrics',
	'ID3v2LyricsFrame',
	'ID3v2NumberFrame',
	'ID3v2NumericTextFrame',
	'ID3v2OWNEFrame',
	'ID3v2OwnershipTransaction',
	'ID3v2PICFrame',
	'ID3v2PeopleListFrame',
	'ID3v2Performer',
	'ID3v2Picture',
	'ID3v2PlayCounterFrame',
	'ID3v2Popularimeter',
	'ID3v2PopularimeterFrame',
	'ID3v2PrivateFrame',
	'ID3v2PrivateInfo',
	'ID3v2RecommendedBuffer',
	'ID3v2RecommendedBufferFrame',
	'ID3v2SynchronizedLyrics',
	'ID3v2SynchronizedLyricsFrame',
	'ID3v2SynchronizedTempoCodes',
	'ID3v2SynchronizedTempoCodesFrame',
	'ID3v2TMCLFrame',
	'ID3v2TPROFrame',
	'ID3v2TermsOfUse',
	'ID3v2TextFrame',
	'ID3v2TimeFrame',
	'ID3v2TimestampFrame',
	'ID3v2Track',
	'ID3v2TrackFrame',
	'ID3v2URLLinkFrame',
	'ID3v2USERFrame',
	'ID3v2UniqueFileIdentifier',
	'ID3v2UniqueFileIdentifierFrame',
	'ID3v2UnsynchronizedLyrics',
	'ID3v2UnsynchronizedLyricsFrame',
	'ID3v2UserText',
	'ID3v2UserTextFrame',
	'ID3v2UserURLLink',
	'ID3v2UserURLLinkFrame',
	'ID3v2YearFrame',
]

import os
import re
import string
import struct
import warnings
import zlib
from urllib.parse import unquote

import bitstruct
import more_itertools
from attr import (
	attrib,
	attrs,
)
from pendulum.parsing import ParserError
from pendulum.parsing.iso8601 import parse_iso8601
from tbm_utils import (
	AttrMapping,
	datareader,
)

from .tables import (
	ID3PictureType,
	ID3Version,
	ID3v1Genres,
	ID3v2EventTypes,
	ID3v2LyricsContentType,
	ID3v2TimestampFormat,
)
from ..exceptions import (
	AudioMetadataWarning,
	FormatError,
	TagError,
	UnsupportedFormat,
)
from ..models import (
	Picture,
	Tag,
)
from ..utils import (
	decode_bytestring,
	decode_synchsafe_int,
	determine_encoding,
	get_image_size,
	remove_unsynchronization,
	split_encoded,
)

_genre_re = re.compile(r"((?:\((?P<id>\d+|RX|CR)\))*)(?P<name>.+)?")


##########
# Models #
##########

@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2AudioEncryption(AttrMapping):
	owner = attrib()
	preview_start = attrib()
	preview_size = attrib()
	info = attrib()


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2Comment(AttrMapping):
	language = attrib()
	description = attrib()
	text = attrib()


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2Disc(AttrMapping):
	number = attrib()
	total = attrib(default=None)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2Event(AttrMapping):
	type = attrib()  # noqa
	timestamp = attrib()


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2Events(AttrMapping):
	timestamp_format = attrib(converter=ID3v2TimestampFormat)
	events = attrib()


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2GeneralEncapsulatedObject(AttrMapping):
	mime_type = attrib()
	filename = attrib()
	description = attrib()
	object = attrib()  # noqa


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2GroupID(AttrMapping):
	owner = attrib()
	symbol = attrib()
	data = attrib()


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2InvolvedPerson(AttrMapping):
	involvement = attrib()
	name = attrib()


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2Lyrics(AttrMapping):
	language = attrib()
	description = attrib()
	text = attrib()


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2SynchronizedLyrics(ID3v2Lyrics):
	timestamp_format = attrib(converter=ID3v2TimestampFormat)
	content_type = attrib(converter=ID3v2LyricsContentType)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2UnsynchronizedLyrics(ID3v2Lyrics):
	pass


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2OwnershipTransaction(AttrMapping):
	price_paid = attrib()
	date_of_purchase = attrib()
	seller = attrib()


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2Performer(AttrMapping):
	instrument = attrib()
	name = attrib()


class ID3v2Picture(Picture):
	@datareader
	@classmethod
	def parse(cls, data, *, id3v22=False):
		data = data.read()

		encoding = determine_encoding(data[0:1])

		if id3v22:
			mime_type = decode_bytestring(data[1:4])
			mime_end = 3
		else:
			mime_end = data[1:].index(b'\x00', 0) + 1
			mime_type = decode_bytestring(data[1:mime_end])

		type_ = ID3PictureType(data[mime_end + 1])

		try:
			description, image_data = split_encoded(data[mime_end + 2:], encoding, 1)
		except ValueError:
			raise FormatError("Missing data in ID3v2 picture.") from None
		else:
			if not image_data.strip(b'\x00'):
				raise FormatError("No image data in picture frame.")

		description = decode_bytestring(description, encoding)
		try:
			width, height = get_image_size(image_data)
		except ValueError:
			raise FormatError("Missing width/height in ID3v2 picture.") from None

		return cls(
			type=type_,
			mime_type=mime_type,
			description=description,
			width=width,
			height=height,
			data=image_data,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2Popularimeter(AttrMapping):
	email = attrib()
	rating = attrib()
	count = attrib(default=None)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2PrivateInfo(AttrMapping):
	owner = attrib()
	data = attrib()


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2RecommendedBuffer(AttrMapping):
	size = attrib()
	embedded = attrib(converter=bool)
	offset = attrib(default=None)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2SynchronizedTempoCodes(AttrMapping):
	timestamp_format = attrib(converter=ID3v2TimestampFormat)
	data = attrib()


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2TermsOfUse(AttrMapping):
	language = attrib()
	text = attrib()


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2Track(AttrMapping):
	number = attrib()
	total = attrib(default=None)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2UniqueFileIdentifier(AttrMapping):
	owner = attrib()
	identifier = attrib()


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2UserText(AttrMapping):
	description = attrib()
	text = attrib()


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2UserURLLink(AttrMapping):
	description = attrib()
	url = attrib()


########
# Base #
########

@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2FrameFlags(AttrMapping):
	alter_tag = attrib(default=False, converter=bool)
	alter_file = attrib(default=False, converter=bool)
	read_only = attrib(default=False, converter=bool)
	grouped = attrib(default=False, converter=bool)
	compressed = attrib(default=False, converter=bool)
	encrypted = attrib(default=False, converter=bool)
	unsync = attrib(default=False, converter=bool)
	data_length_indicator = attrib(default=False, converter=bool)

	@datareader
	@classmethod
	def parse(cls, data, id3_version):
		id3_version = ID3Version(id3_version)
		if id3_version not in [
			ID3Version.v23,
			ID3Version.v24,
		]:
			raise ValueError(f"Frame flags not supported for ID3 version: {id3_version}.")  # pragma: nocover

		if id3_version is ID3Version.v24:
			flags = bitstruct.unpack_dict(
				'p1 b1 b1 b1 p5 b1 p2 b1 b1 b1 b1',
				[
					'alter_tag',
					'alter_file',
					'read_only',
					'grouped',
					'compressed',
					'encrypted',
					'unsync',
					'data_length_indicator',
				],
				data.read(2),
			)
		else:
			flags = bitstruct.unpack_dict(
				'b1 b1 b1 p5 b1 b1 b1 p5',
				[
					'alter_tag',
					'alter_file',
					'read_only',
					'compressed',
					'encrypted',
					'grouped',
				],
				data.read(2),
			)

		return cls(**flags)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2Frame(Tag):
	encoding = attrib(default=None)

	@datareader
	@staticmethod
	def _parse_frame_data(data):
		return (
			data.read(),
			None,
		)

	@datareader
	@staticmethod
	def _parse_frame_header(data, id3_version):
		id3_version = ID3Version(id3_version)
		if id3_version not in [
			ID3Version.v22,
			ID3Version.v23,
			ID3Version.v24,
		]:
			raise ValueError(f"Unsupported ID3 version: {id3_version}.")  # pragma: nocover

		flags = None
		if id3_version is ID3Version.v24:
			try:
				id_, size, flags = struct.unpack(
					'4s4s2s',
					data.read(10),
				)
			except struct.error:
				raise FormatError("Not enough data.")

			frame_size = decode_synchsafe_int(size, 7)
		elif id3_version is ID3Version.v23:
			try:
				id_, frame_size, flags = struct.unpack(
					'>4sI2s',
					data.read(10),
				)
			except struct.error:
				raise FormatError("Not enough data.")
		elif id3_version is ID3Version.v22:  # pragma: nobranch
			try:
				id_, size = struct.unpack(
					'3s3s',
					data.read(6),
				)
			except struct.error:
				raise FormatError("Not enough data.")

			frame_size = struct.unpack(
				'>I',
				b'\x00' + size,
			)[0]

		if frame_size <= 0:
			raise FormatError("ID3v2 frame size must be greater than 0.")

		if flags is not None:
			frame_flags = ID3v2FrameFlags.parse(flags, id3_version)
		else:
			frame_flags = ID3v2FrameFlags()

		frame_id = id_.decode('iso-8859-1')

		return frame_id, frame_size, frame_flags

	@datareader
	@classmethod
	def parse(cls, data, id3_version, unsync):
		id3_version = ID3Version(id3_version)
		if id3_version not in [
			ID3Version.v22,
			ID3Version.v23,
			ID3Version.v24,
		]:
			raise ValueError(f"Unsupported ID3 version: {id3_version}.")  # pragma: nocover

		frame_id, frame_size, frame_flags = ID3v2Frame._parse_frame_header(
			data,
			id3_version,
		)

		if frame_flags.encrypted:
			raise UnsupportedFormat("ID3v2 frame encryption is not supported.")

		if frame_flags.compressed:
			if not frame_flags.data_length_indicator:
				raise FormatError("ID3v2 frame compression flag set without data length indicator.")

			data.seek(4, os.SEEK_CUR)

		frame_type = ID3v2FrameTypes.get(frame_id, ID3v2Frame)

		if (
			unsync
			or frame_flags.unsync
		):
			read_size = frame_size
			frame_data = remove_unsynchronization(data.read(read_size))
			while len(frame_data) < frame_size:
				data.seek(-read_size, os.SEEK_CUR)
				read_size += 1
				frame_data = remove_unsynchronization(data.read(read_size))
		else:
			frame_data = data.read(frame_size)

		if frame_flags.compressed:
			frame_data = zlib.decompress(frame_data)

		try:
			frame_value, frame_encoding = frame_type._parse_frame_data(frame_data)

			if not frame_value:
				raise TagError(f"No value found in ``{frame_id}`` frame.")

			return frame_type(
				name=frame_id,
				value=frame_value,
				encoding=frame_encoding,
			)
		except (TypeError, TagError) as exc:  # Bad frame value.
			warnings.warn(
				(
					f"Ignoring ``{frame_id}``.\n"
					f"{exc}\n"
				),
				AudioMetadataWarning,
			)

			return None


######################
# Binary Data Frames #
######################

@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2BinaryDataFrame(ID3v2Frame):
	pass


##############################
# Complex Binary Data Frames #
##############################


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2AudioEncryptionFrame(ID3v2Frame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		owner, remainder = frame_data.split(b'\x00', 1)
		preview_start, preview_size = struct.unpack('>HH', remainder[0:4])

		return (
			ID3v2AudioEncryption(
				owner=owner.decode('iso-8859-1'),
				preview_start=preview_start,
				preview_size=preview_size,
				info=remainder[4:],
			),
			None,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2GRIDFrame(ID3v2Frame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()
		owner, remainder = frame_data.split(b'\x00', 1)
		symbol = remainder[0:1]

		if (
			symbol < b'\x80'
			or symbol > b'\xF0'
		):
			raise TagError(f"Invalid group symbol in ID3v2 ``GRID`` frame: {symbol}")

		return (
			ID3v2GroupID(
				owner=owner.decode('iso-8859-1'),
				symbol=symbol,
				data=remainder[1:],
			),
			None,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2GeneralEncapsulatedObjectFrame(ID3v2Frame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		encoding = determine_encoding(frame_data)

		try:
			mime_type, filename, description, object_ = split_encoded(frame_data[1:], encoding, 3)
		except ValueError:
			raise TagError("Missing data in general encapsulated object frame.")

		return (
			ID3v2GeneralEncapsulatedObject(
				mime_type=mime_type,
				filename=filename,
				description=description,
				object=object_,
			),
			encoding,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2PrivateFrame(ID3v2Frame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()
		owner_end = frame_data.index(b'\x00')

		return (
			ID3v2PrivateInfo(
				owner=frame_data[0:owner_end].decode('iso-8859-1'),
				data=frame_data[owner_end + 1:],
			),
			None,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2SynchronizedTempoCodesFrame(ID3v2Frame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		return (
			ID3v2SynchronizedTempoCodes(
				timestamp_format=ID3v2TimestampFormat(frame_data[0]),
				data=frame_data[1:]
			),
			None,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2UniqueFileIdentifierFrame(ID3v2Frame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()
		owner, identifier = frame_data.split(b'\x00', 1)

		if len(identifier) > 64:
			raise TagError("ID3v2 unique file identifier must be no more than 64 bytes.")

		return (
			ID3v2UniqueFileIdentifier(
				owner=owner.decode('iso-8859-1'),
				identifier=identifier,
			),
			None,
		)


#######################
# Complex Text Frames #
#######################

@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2PeopleListFrame(ID3v2Frame):
	pass


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2CommentFrame(ID3v2Frame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		encoding = determine_encoding(frame_data)

		try:
			description, value = split_encoded(frame_data[4:], encoding, 1)
		except ValueError:
			raise TagError("Missing data in comment frame.") from None
		else:
			if not value:
				raise TagError("No comment found in comment frame.")

		comment = ID3v2Comment(
			language=decode_bytestring(frame_data[1:4]),
			description=decode_bytestring(description, encoding),
			text=decode_bytestring(value, encoding),
		)

		return (
			comment,
			encoding,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2GenreFrame(ID3v2Frame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		encoding = determine_encoding(frame_data)

		try:
			values = [
				decode_bytestring(value, encoding)
				for value in split_encoded(frame_data[1:], encoding)
				if value
			]
		except ValueError:
			raise TagError("Missing data in genre frame.") from None
		else:
			if not values:
				raise TagError("No genres found in genre frame.")

		genres = []
		for value in values:
			if value.isdigit():
				try:
					genres.append(ID3v1Genres[int(value)])
				except IndexError:
					genres.append(value)
			elif value == 'CR':
				genres.append('Cover')
			elif value == 'RX':
				genres.append('Remix')
			else:
				match = _genre_re.match(value)

				if match['id']:
					if match['id'].isdigit():
						try:
							genres.append(ID3v1Genres[int(match['id'])])
						except IndexError:
							genres.append(value)
					elif match['id'] == 'CR':
						genres.append('Cover')
					elif match['id'] == 'RX':
						genres.append('Remix')
					else:
						genres.append(value)

				if match['name']:
					if match['name'].startswith("(("):
						genres.append(match['name'][1:])
					elif match['name'] not in genres:
						genres.append(match['name'])

		return (
			genres,
			encoding,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2InvolvedPeopleListFrame(ID3v2PeopleListFrame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		encoding = determine_encoding(frame_data)

		try:
			values = list(
				more_itertools.sliced(
					split_encoded(frame_data[1:], encoding),
					2,
				)
			)
		except ValueError:
			raise TagError("Missing data found in involved people list frame.") from None

		if len(values) < 1:
			raise TagError("No people found in involved people list frame.")

		people = [
			ID3v2InvolvedPerson(
				involvement=decode_bytestring(involvement, encoding),
				name=decode_bytestring(name, encoding),
			)
			for involvement, name in values
		]

		return (
			people,
			encoding,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2OWNEFrame(ID3v2Frame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		encoding = determine_encoding(frame_data)

		price_paid, remainder = frame_data[1:].split(b'\x00', 1)

		date_of_purchase = remainder[:8].decode('iso-8859-1')
		if not date_of_purchase.is_digit():
			raise TagError("ID3v2 ``OWNE`` frame date of purchase must be in the form of ``YYYYMMDD``.")

		return (
			ID3v2OwnershipTransaction(
				price_paid=price_paid.decode('iso-8859-1'),
				date_of_purchase=date_of_purchase,
				seller=decode_bytestring(remainder[8:], encoding),
			),
			encoding,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2TMCLFrame(ID3v2InvolvedPeopleListFrame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		encoding = determine_encoding(frame_data)

		try:
			values = list(
				more_itertools.sliced(
					split_encoded(frame_data[1:], encoding),
					2,
				)
			)
		except ValueError:
			raise TagError("Missing data in TMCL frame.") from None

		if len(values) < 1:
			raise TagError("No musicians found in TMCL frame.")

		performers = [
			ID3v2Performer(
				instrument=decode_bytestring(instrument, encoding),
				name=decode_bytestring(name, encoding),
			)
			for instrument, name in values
		]

		return (
			performers,
			encoding,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2USERFrame(ID3v2Frame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		encoding = determine_encoding(frame_data)

		return (
			ID3v2TermsOfUse(
				language=decode_bytestring(frame_data[1:4]),
				text=decode_bytestring(frame_data[4:], encoding),
			),
			encoding,
		)


#################
# Lyrics Frames #
#################

@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2LyricsFrame(ID3v2Frame):
	pass


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2SynchronizedLyricsFrame(ID3v2LyricsFrame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		encoding = determine_encoding(frame_data)

		try:
			description, text = split_encoded(frame_data[6:], encoding)
		except ValueError:
			raise TagError("Missing data in synchronized lyrics frame.") from None
		else:
			if not text:
				raise TagError("No lyrics found in synchronized lyrics frame.")

		return (
			ID3v2SynchronizedLyrics(
				language=decode_bytestring(frame_data[1:4]),
				description=decode_bytestring(description, encoding),
				text=decode_bytestring(text, encoding),
				timestamp_format=ID3v2TimestampFormat(frame_data[4]),
				content_type=frame_data[5],
			),
			encoding,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2UnsynchronizedLyricsFrame(ID3v2LyricsFrame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		encoding = determine_encoding(frame_data)

		try:
			description, text = split_encoded(frame_data[4:], encoding)
		except ValueError:
			raise TagError("Missing data in unsynchronized lyrics frame.")
		else:
			if not text:
				raise TagError("No lyrics found in unsynchronized lyrics frame.")

		return (
			ID3v2UnsynchronizedLyrics(
				language=decode_bytestring(frame_data[1:4]),
				description=decode_bytestring(description, encoding),
				text=decode_bytestring(text, encoding)
			),
			encoding,
		)


#################
# Number Frames #
#################

@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2NumberFrame(ID3v2Frame):
	def _validate_value(value):
		if not all(char in [*string.digits, '/'] for char in value):
			raise TagError(
				"Number frame values must consist only of digits and '/'.",
			)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2DiscFrame(ID3v2NumberFrame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		encoding = determine_encoding(frame_data)

		value = decode_bytestring(frame_data[1:], encoding)
		ID3v2NumberFrame._validate_value(value)

		values = value.split('/')
		number = values[0]
		total = values[1] if len(values) == 2 else None

		return (
			ID3v2Disc(
				number=number,
				total=total,
			),
			encoding,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2TrackFrame(ID3v2NumberFrame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		encoding = determine_encoding(frame_data)

		value = decode_bytestring(frame_data[1:], encoding)
		ID3v2NumberFrame._validate_value(value)

		values = value.split('/')
		number = values[0]
		total = values[1] if len(values) == 2 else None

		return (
			ID3v2Track(
				number=number,
				total=total,
			),
			encoding,
		)


#######################
# Numeric Text Frames #
#######################

@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2NumericTextFrame(ID3v2Frame):
	value = attrib()

	@value.validator
	def _validate_value(self, attribute, value):
		if not all(v.isdigit() for v in value):
			raise TagError("Numeric text frame values must consist only of digits.")

	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		encoding = determine_encoding(frame_data)

		try:
			values = [
				decode_bytestring(value, encoding)
				for value in split_encoded(frame_data[1:], encoding)
				if value
			]
		except ValueError:
			raise TagError("Missing data in numeric text frame.") from None
		else:
			if not values:
				raise TagError("No values found in numeric text frame.")

		return (
			values,
			encoding,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2DateFrame(ID3v2NumericTextFrame):
	value = attrib()

	@value.validator
	def _validate_value(self, attribute, value):
		if not all(
			(
				v.isdigit()
				and len(v) == 4
				and int(v[0:2]) in range(1, 32)
				and int(v[2:4]) in range(1, 13)
			)
			for v in value
		):
			raise TagError(
				"ID3v2 date frame values must be a 4-character number string in the ``DDMM`` format.",
			)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2TimeFrame(ID3v2NumericTextFrame):
	value = attrib()

	@value.validator
	def _validate_value(self, attribute, value):
		if not all(
			(
				v.isdigit()
				and len(v) == 4
				and int(v[0:2]) in range(0, 24)
				and int(v[2:4]) in range(0, 60)
			)
			for v in value
		):
			raise TagError(
				"ID3v2 ``TIME`` frame values must be a 4-character number string in the ``HHMM`` format.",
			)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2YearFrame(ID3v2NumericTextFrame):
	value = attrib()

	@value.validator
	def _validate_value(self, attribute, value):
		if not all(
			(
				v.isdigit()
				and len(v) == 4
			)
			for v in value
		):
			raise TagError("Year frame values must be 4-character number strings.")


################
# Other Frames #
################

@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2EventTimingCodesFrame(ID3v2Frame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		timestamp_format = ID3v2TimestampFormat(frame_data[0])

		remaining = frame_data[1:]
		events = []
		while len(remaining) >= 5:
			type_, timestamp = struct.unpack('>bI', remaining[:5])
			event_type = ID3v2EventTypes(type_)

			events.append(
				ID3v2Event(
					type=event_type,
					timestamp=timestamp,
				)
			)

			remaining = remaining[5:]

		return (
			ID3v2Events(
				timestamp_format=timestamp_format,
				events=events,
			),
			None,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2PlayCounterFrame(ID3v2Frame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		if len(frame_data) < 4:
			raise TagError("Play count must be at least 4 bytes long.")

		return (
			int.from_bytes(frame_data, byteorder='big'),
			None,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2PopularimeterFrame(ID3v2Frame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		email, remainder = frame_data.split(b'\x00', 1)
		rating = remainder[0]
		remainder = remainder[1:]

		if not remainder:
			count = None
		else:
			if len(remainder) < 4:
				raise TagError("Popularimeter count must be at least 4 bytes long.")

			count = int.from_bytes(remainder, byteorder='big')

		return (
			ID3v2Popularimeter(
				email=email.decode('iso-8859-1'),
				rating=rating,
				count=count,
			),
			None,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2RecommendedBufferFrame(ID3v2Frame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		size = int.from_bytes(frame_data[0:3], byteorder='big')
		embedded = bitstruct.unpack('>p7 b1', frame_data[3:4])
		if embedded:
			offset = struct.unpack('>I', frame_data[4:])
		else:
			offset = None

		return (
			ID3v2RecommendedBuffer(
				size=size,
				embedded=embedded,
				offset=offset,
			),
			None,
		)


##################
# Picture Frames #
##################

@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2APICFrame(ID3v2Frame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		try:
			picture = ID3v2Picture.parse(frame_data)
		except FormatError as exc:
			raise TagError(str(exc)) from None

		return (
			picture,
			None,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2PICFrame(ID3v2Frame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		try:
			picture = ID3v2Picture.parse(frame_data, id3v22=True)
		except FormatError as exc:
			raise TagError(str(exc)) from None

		return (
			picture,
			None,
		)


###############
# Text Frames #
###############

@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2TextFrame(ID3v2Frame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		encoding = determine_encoding(frame_data)

		try:
			values = [
				decode_bytestring(value, encoding)
				for value in split_encoded(frame_data[1:], encoding)
				if value
			]
		except ValueError:
			raise TagError("Missing data in text frame.") from None
		else:
			if not values:
				raise TagError("No values found in text frame.")

		return (
			values,
			encoding,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2TimestampFrame(ID3v2Frame):
	value = attrib()

	@value.validator
	def _validate_value(self, attribute, value):
		for v in value:
			try:
				parse_iso8601(v)
			except ParserError:
				raise TagError("Timestamp frame values must conform to the ID3v2-compliant subset of ISO 8601.")

	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		encoding = determine_encoding(frame_data)

		try:
			values = [
				decode_bytestring(value, encoding)
				for value in split_encoded(frame_data[1:], encoding)
				if value
			]
		except ValueError:
			raise TagError("Missing data in timestamp frame.") from None
		else:
			if not values:
				raise TagError("No values found in timestamp frame.")

		return (
			values,
			encoding,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2TPROFrame(ID3v2TextFrame):
	value = attrib()

	@value.validator
	def _validate_value(self, attribute, value):
		if (
			not all(
				v.isdigit()
				for v in value[0:4]
			)
			or not value[4] == ' '
		):
			raise TagError("TPRO frame values must start with a year followed by a space.")


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2UserTextFrame(ID3v2Frame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		encoding = determine_encoding(frame_data)

		try:
			description, *remainder = split_encoded(frame_data[1:], encoding)
		except ValueError:
			raise TagError("Missing data in user text frame.") from None

		values = [
			decode_bytestring(value, encoding)
			for value in remainder
			if value
		]

		if not values:
			raise TagError("No values found in user text frame.")

		return (
			ID3v2UserText(
				description=decode_bytestring(description, encoding),
				text=values,
			),
			encoding,
		)


###################
# URL Link Frames #
###################

@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2URLLinkFrame(ID3v2Frame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		return (
			unquote(decode_bytestring(frame_data)),
			None,
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v2UserURLLinkFrame(ID3v2Frame):
	@datareader
	@staticmethod
	def _parse_frame_data(data):
		frame_data = data.read()

		encoding = determine_encoding(frame_data)

		try:
			description, url = split_encoded(frame_data[1:], encoding, 1)
		except ValueError:
			raise TagError("Missing data in user URL link frame.") from None
		else:
			if not url:
				raise TagError("No URL found in user URL link frame.")

		return (
			ID3v2UserURLLink(
				description=decode_bytestring(description, encoding),
				url=unquote(decode_bytestring(url)),
			),
			encoding,
		)


# TODO:ID3v2.2
# TODO: CRM, EQU, LNK, MCI, MLL, REV, RVA

# TODO: ID3v2.3
# TODO: COMR, ENCR, EQUA, LINK, MLLT
# TODO: POSS, RGAD, RVAD, RVRB, XRVA

# TODO: ID3v2.4
# TODO: ASPI, COMR, ENCR, EQU2, LINK, MLLT,
# TODO: POSS, RGAD, RVA2, RVRB, SEEK, SIGN, XRVA
ID3v2FrameTypes = {
	# Binary data frames
	'PCS': ID3v2BinaryDataFrame,

	'MCDI': ID3v2BinaryDataFrame,
	'NCON': ID3v2BinaryDataFrame,
	'PCST': ID3v2BinaryDataFrame,

	# Complex binary data frames
	'CRA': ID3v2AudioEncryptionFrame,
	'GEO': ID3v2GeneralEncapsulatedObjectFrame,
	'STC': ID3v2SynchronizedTempoCodesFrame,
	'UFI': ID3v2UniqueFileIdentifierFrame,

	'AENC': ID3v2AudioEncryptionFrame,
	'GEOB': ID3v2GeneralEncapsulatedObjectFrame,
	'GRID': ID3v2GRIDFrame,
	'PRIV': ID3v2PrivateFrame,
	'SYTC': ID3v2SynchronizedTempoCodesFrame,
	'UFID': ID3v2UniqueFileIdentifierFrame,

	# Complex Text Frames
	'COM': ID3v2CommentFrame,
	'IPL': ID3v2InvolvedPeopleListFrame,
	'TCO': ID3v2GenreFrame,

	'COMM': ID3v2CommentFrame,
	'IPLS': ID3v2InvolvedPeopleListFrame,
	'OWNE': ID3v2OWNEFrame,
	'TCON': ID3v2GenreFrame,
	'TIPL': ID3v2InvolvedPeopleListFrame,
	'TMCL': ID3v2TMCLFrame,
	'USER': ID3v2USERFrame,

	# Lyrics Frames
	'SLT': ID3v2SynchronizedLyricsFrame,
	'ULT': ID3v2UnsynchronizedLyricsFrame,

	'SYLT': ID3v2SynchronizedLyricsFrame,
	'USLT': ID3v2UnsynchronizedLyricsFrame,

	# Number Frames
	'TPA': ID3v2DiscFrame,
	'TRK': ID3v2TrackFrame,

	'TPOS': ID3v2DiscFrame,
	'TRCK': ID3v2TrackFrame,

	# Numeric Text Frames
	'TBP': ID3v2NumericTextFrame,
	'TDA': ID3v2DateFrame,
	'TDY': ID3v2NumericTextFrame,
	'TIM': ID3v2TimeFrame,
	'TLE': ID3v2NumericTextFrame,
	'TOR': ID3v2YearFrame,
	'TSI': ID3v2NumericTextFrame,
	'TYE': ID3v2YearFrame,

	'TBPM': ID3v2NumericTextFrame,
	'TDAT': ID3v2DateFrame,
	'TDLY': ID3v2NumericTextFrame,
	'TIME': ID3v2TimeFrame,
	'TLEN': ID3v2NumericTextFrame,
	'TORY': ID3v2YearFrame,
	'TSIZ': ID3v2NumericTextFrame,
	'TYER': ID3v2YearFrame,

	# Other Frames
	'BUF': ID3v2RecommendedBufferFrame,
	'CNT': ID3v2PlayCounterFrame,
	'ETC': ID3v2EventTimingCodesFrame,
	'POP': ID3v2PopularimeterFrame,

	'ETCO': ID3v2EventTimingCodesFrame,
	'PCNT': ID3v2PlayCounterFrame,
	'POPM': ID3v2PopularimeterFrame,
	'RBUF': ID3v2RecommendedBufferFrame,

	# Picture Frames
	'PIC': ID3v2PICFrame,

	'APIC': ID3v2APICFrame,

	# Text Frames
	'TAL': ID3v2TextFrame,
	'TCM': ID3v2TextFrame,
	'TCR': ID3v2TextFrame,
	'TDS': ID3v2TextFrame,
	'TEN': ID3v2TextFrame,
	'TFT': ID3v2TextFrame,
	'TKE': ID3v2TextFrame,
	'TLA': ID3v2TextFrame,
	'TMT': ID3v2TextFrame,
	'TOA': ID3v2TextFrame,
	'TOF': ID3v2TextFrame,
	'TOL': ID3v2TextFrame,
	'TOT': ID3v2TextFrame,
	'TP1': ID3v2TextFrame,
	'TP2': ID3v2TextFrame,
	'TP3': ID3v2TextFrame,
	'TP4': ID3v2TextFrame,
	'TPB': ID3v2TextFrame,
	'TRC': ID3v2TextFrame,
	'TRD': ID3v2TextFrame,
	'TS2': ID3v2TextFrame,
	'TSA': ID3v2TextFrame,
	'TSC': ID3v2TextFrame,
	'TSP': ID3v2TextFrame,
	'TSS': ID3v2TextFrame,
	'TST': ID3v2TextFrame,
	'TT1': ID3v2TextFrame,
	'TT2': ID3v2TextFrame,
	'TT3': ID3v2TextFrame,
	'TXT': ID3v2TextFrame,
	'TXX': ID3v2UserTextFrame,

	'GRP1': ID3v2TextFrame,
	'TALB': ID3v2TextFrame,
	'TCAT': ID3v2TextFrame,
	'TCMP': ID3v2TextFrame,
	'TCOM': ID3v2TextFrame,
	'TCOP': ID3v2TextFrame,
	'TDES': ID3v2TextFrame,
	'TENC': ID3v2TextFrame,
	'TEXT': ID3v2TextFrame,
	'TFLT': ID3v2TextFrame,
	'TIT1': ID3v2TextFrame,
	'TIT2': ID3v2TextFrame,
	'TIT3': ID3v2TextFrame,
	'TKEY': ID3v2TextFrame,
	'TKWD': ID3v2TextFrame,
	'TLAN': ID3v2TextFrame,
	'TMED': ID3v2TextFrame,
	'TMOO': ID3v2TextFrame,
	'TOAL': ID3v2TextFrame,
	'TOFN': ID3v2TextFrame,
	'TOLY': ID3v2TextFrame,
	'TOPE': ID3v2TextFrame,
	'TOWN': ID3v2TextFrame,
	'TPE1': ID3v2TextFrame,
	'TPE2': ID3v2TextFrame,
	'TPE3': ID3v2TextFrame,
	'TPE4': ID3v2TextFrame,
	'TPRO': ID3v2TPROFrame,
	'TPUB': ID3v2TextFrame,
	'TRDA': ID3v2TextFrame,
	'TRSN': ID3v2TextFrame,
	'TRSO': ID3v2TextFrame,
	'TSO2': ID3v2TextFrame,
	'TSOA': ID3v2TextFrame,
	'TSOC': ID3v2TextFrame,
	'TSOP': ID3v2TextFrame,
	'TSOT': ID3v2TextFrame,
	'TSRC': ID3v2TextFrame,
	'TSSE': ID3v2TextFrame,
	'TSST': ID3v2TextFrame,
	'TXXX': ID3v2UserTextFrame,
	'XSOA': ID3v2TextFrame,
	'XSOP': ID3v2TextFrame,
	'XSOT': ID3v2TextFrame,

	# Timestamp Frames
	'TDR': ID3v2TimestampFrame,

	'TDEN': ID3v2TimestampFrame,
	'TDOR': ID3v2TimestampFrame,
	'TDRC': ID3v2TimestampFrame,
	'TDRL': ID3v2TimestampFrame,
	'TDTG': ID3v2TimestampFrame,
	'XDOR': ID3v2TimestampFrame,

	# URL Link Frames
	'TID': ID3v2URLLinkFrame,
	'WAF': ID3v2URLLinkFrame,
	'WAR': ID3v2URLLinkFrame,
	'WAS': ID3v2URLLinkFrame,
	'WCM': ID3v2URLLinkFrame,
	'WCP': ID3v2URLLinkFrame,
	'WFD': ID3v2URLLinkFrame,
	'WPB': ID3v2URLLinkFrame,
	'WXX': ID3v2UserURLLinkFrame,

	'TGID': ID3v2URLLinkFrame,
	'WCOM': ID3v2URLLinkFrame,
	'WCOP': ID3v2URLLinkFrame,
	'WFED': ID3v2URLLinkFrame,
	'WOAF': ID3v2URLLinkFrame,
	'WOAR': ID3v2URLLinkFrame,
	'WOAS': ID3v2URLLinkFrame,
	'WORS': ID3v2URLLinkFrame,
	'WPAY': ID3v2URLLinkFrame,
	'WPUB': ID3v2URLLinkFrame,
	'WXXX': ID3v2UserURLLinkFrame,
}
