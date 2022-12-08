# http://id3.org/ID3v1

__all__ = [
	'ID3v1',
	'ID3v1AlbumField',
	'ID3v1ArtistField',
	'ID3v1CommentField',
	'ID3v1Field',
	'ID3v1Fields',
	'ID3v1GenreField',
	'ID3v1TitleField',
	'ID3v1TrackNumberField',
	'ID3v1YearField',
]

from attr import (
	attrib,
	attrs,
)
from tbm_utils import (
	AttrMapping,
	datareader,
)

from .tables import ID3v1Genres
from ..exceptions import FormatError
from ..models import (
	Tag,
	Tags,
)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v1Field(Tag):
	pass


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v1AlbumField(Tag):
	@datareader
	@classmethod
	def parse(cls, data):
		return cls(
			name='album',
			value=data.read(30).strip(b'\x00').decode('iso-8859-1'),
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v1ArtistField(Tag):
	@datareader
	@classmethod
	def parse(cls, data):
		return cls(
			name='artist',
			value=data.read(30).strip(b'\x00').decode('iso-8859-1'),
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v1CommentField(Tag):
	@datareader
	@classmethod
	def parse(cls, data):
		return cls(
			name='comment',
			value=data.read(29).strip(b'\x00').decode('iso-8859-1'),
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v1GenreField(Tag):
	value = attrib(converter=lambda v: ID3v1Genres[v])

	@datareader
	@classmethod
	def parse(cls, data):
		return cls(
			name='genre',
			value=int.from_bytes(data.read(1), byteorder='big'),
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v1TitleField(Tag):
	@datareader
	@classmethod
	def parse(cls, data):
		return cls(
			name='title',
			value=data.read(30).strip(b'\x00').decode('iso-8859-1'),
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v1TrackNumberField(Tag):
	@datareader
	@classmethod
	def parse(cls, data):
		return cls(
			name='tracknumber',
			value=str(data.read(1)[0]),
		)


@attrs(
	repr=False,
	kw_only=True,
)
class ID3v1YearField(Tag):
	@datareader
	@classmethod
	def parse(cls, data):
		return cls(
			name='year',
			value=data.read(4).strip(b'\x00').decode('iso-8859-1'),
		)


class ID3v1Fields(Tags):
	@datareader
	@classmethod
	def parse(cls, data):
		self = cls()

		title = ID3v1TitleField.parse(data).value
		artist = ID3v1ArtistField.parse(data).value
		album = ID3v1AlbumField.parse(data).value
		year = ID3v1YearField.parse(data).value
		comment = ID3v1CommentField.parse(data).value
		tracknumber = ID3v1TrackNumberField.parse(data).value

		try:
			genre = ID3v1GenreField.parse(data).value
		except IndexError:
			pass
		else:
			self.genre = [genre]

		if title:
			self.title = [title]

		if artist:
			self.artist = [artist]

		if album:
			self.album = [album]

		if year:
			self.year = [year]

		if comment:
			self.comment = [comment]

		if tracknumber != '0':
			self.tracknumber = [tracknumber]

		return self


class ID3v1(AttrMapping):
	@datareader
	@classmethod
	def parse(cls, data):
		if data.read(3) != b"TAG":
			raise FormatError("Valid ID3v1 header not found.")

		self = cls()
		self.tags = ID3v1Fields.parse(data)

		return self
