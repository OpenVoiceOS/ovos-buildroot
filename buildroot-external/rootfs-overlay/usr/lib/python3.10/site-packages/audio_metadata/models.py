__all__ = [
	'Format',
	'Picture',
	'StreamInfo',
	'Tag',
	'Tags',
]

import os

from attr import (
	attrib,
	attrs,
)
from bidict import frozenbidict
from tbm_utils import (
	AttrMapping,
	datareader,
	humanize_filesize,
)

from .utils import (
	humanize_bitrate,
	humanize_duration,
	humanize_sample_rate,
)


@attrs(
	repr=False,
	kw_only=True,
)
class Tag(AttrMapping):
	name = attrib()
	value = attrib()


class Tags(AttrMapping):
	"""Base class for tags objects.

	Attributes:
		FIELD_MAP (frozenbidict): A mapping of format-specific
			field names to common aliases.
	"""

	FIELD_MAP = frozenbidict()

	def __getattr__(self, attr):
		a = self.FIELD_MAP.get(attr, attr)

		return super().__getattr__(a)

	def __setattr__(self, attr, value):
		a = self.FIELD_MAP.get(attr, attr)

		super().__setattr__(a, value)

	def __delattr__(self, attr):
		a = self.FIELD_MAP.get(attr, attr)

		super().__delattr__(a)

	def __getitem__(self, key):
		k = self.FIELD_MAP.get(key, key)

		return super().__getitem__(k)

	def __setitem__(self, key, value):
		k = self.FIELD_MAP.get(key, key)

		super().__setitem__(k, value)

	def __delitem__(self, key):
		k = self.FIELD_MAP.get(key, key)

		super().__delitem__(k)

	def __iter__(self):
		return iter(
			self.FIELD_MAP.inv.get(k, k)
			for k in self.__dict__
			if not k.startswith('_') and not k == 'FIELD_MAP'
		)

	def __repr__(self, repr_dict=None):
		repr_dict = {
			self.FIELD_MAP.inv.get(k, k): v
			for k, v in self.__dict__.items()
			if not k.startswith('_') and not k == 'FIELD_MAP'
		}

		return super().__repr__(repr_dict=repr_dict)


class Format(AttrMapping):
	"""Base class for audio format objects.

	Attributes:
		filepath (str): Path to audio file, if applicable.
		filesize (int): Size of audio file.
		pictures (list): A list of `Picture` objects.
		tags (Tags): A `Tags` object.
	"""

	tags_type = Tags

	def __init__(self):
		self.filepath = None
		self.filesize = None
		self.pictures = []
		self.tags = self.tags_type()

	def __repr__(self):
		repr_dict = {}

		for k, v in sorted(self.items()):
			if (
				k == 'filesize'
				and v is not None
			):
				repr_dict[k] = humanize_filesize(v, precision=2)
			elif not k.startswith('_'):
				repr_dict[k] = v

		return super().__repr__(repr_dict=repr_dict)

	@datareader
	@classmethod
	def _load(cls, data):
		self = cls()
		self._obj = data

		try:
			self.filepath = os.path.abspath(self._obj.name)
			self.filesize = os.path.getsize(self._obj.name)
		except AttributeError:
			self.filepath = None
			self.filesize = len(self._obj.raw.getbuffer())

		return self


class Picture(AttrMapping):
	"""Base class for picture objects."""

	def __repr__(self):
		repr_dict = {}

		for k, v in sorted(self.items()):
			if k == 'data':
				repr_dict[k] = humanize_filesize(len(v), precision=2)
			elif not k.startswith('_'):
				repr_dict[k] = v

		return super().__repr__(repr_dict=repr_dict)


class StreamInfo(AttrMapping):
	"""Base class for stream information objects."""

	def __repr__(self):
		repr_dict = {}

		for k, v in sorted(self.items()):
			if k.endswith('bitrate'):
				repr_dict[k] = humanize_bitrate(v)
			elif k == 'duration':
				repr_dict[k] = humanize_duration(v)
			elif 'sample_rate' in k:
				repr_dict[k] = humanize_sample_rate(v)
			elif not k.startswith('_'):
				repr_dict[k] = v

		return super().__repr__(repr_dict=repr_dict)
