# https://xiph.org/vorbis/doc/v-comment.html

__all__ = [
	'VorbisComment',
	'VorbisComments',
]

import struct
from collections import defaultdict

from attr import (
	attrib,
	attrs,
)
from tbm_utils import datareader

from ..exceptions import (
	FormatError,
	TagError,
)
from ..models import (
	Tag,
	Tags,
)


@attrs(
	repr=False,
	kw_only=True,
)
class VorbisComment(Tag):
	name = attrib(converter=lambda n: n.lower())

	@staticmethod
	def _validate_name(name):
		return all(
			(
				char >= ' '
				and char <= '}'
				and char != '='
			)
			for char in name
		)

	@datareader
	@classmethod
	def parse(cls, data):
		length = struct.unpack('I', data.read(4))[0]
		comment = data.read(length).decode('utf-8', 'replace')

		if '=' not in comment:
			raise FormatError("Vorbis comment must contain an ``=``.")

		name, value = comment.split('=', 1)

		if not cls._validate_name(name):
			raise TagError(f"Invalid character in Vorbis comment name: ``{name}``.")

		return cls(
			name=name,
			value=value,
		)


# TODO: Number frames.
class VorbisComments(Tags):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		for key in self.keys():
			if not VorbisComment._validate_name(key):
				raise TagError(f"Invalid character in Vorbis comment name: ``{key}``.")

	@datareader
	@classmethod
	def parse(cls, data):
		vendor_length = struct.unpack('I', data.read(4))[0]
		vendor = data.read(vendor_length).decode('utf-8', 'replace')
		num_comments = struct.unpack('I', data.read(4))[0]

		fields = defaultdict(list)

		for _ in range(num_comments):
			comment = VorbisComment.parse(data)
			fields[comment.name].append(comment.value)

		return cls(
			fields,
			_vendor=vendor,
		)
