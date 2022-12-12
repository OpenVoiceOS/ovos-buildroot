__all__ = [
	'AttrMapping',
	'LabelList',
]

from collections import UserList
from collections.abc import (
	ItemsView,
	KeysView,
	MutableMapping,
	ValuesView,
)

import pprintpp


class _KeysView(KeysView):  # pragma: nocover
	def __repr__(self):
		return f"KeysView({pprintpp.pformat(list(self._mapping))})"


class _ItemsView(ItemsView):  # pragma: nocover
	def __repr__(self):
		items = [
			(key, self._mapping[key])
			for key in self._mapping
		]

		return f"ItemsView({pprintpp.pformat(items)})"


class _ValuesView(ValuesView):  # pragma: nocover
	def __repr__(self):
		return f"ValuesView({pprintpp.pformat([self._mapping[key] for key in self._mapping])})"


class AttrMapping(MutableMapping):
	def __init__(self, mapping=None, **kwargs):
		if mapping:
			for k, v in mapping.items():
				self[k] = v

		for k, v in kwargs.items():
			self[k] = v

	def __getattr__(self, attr):
		if attr not in self.__dict__:
			raise AttributeError(attr)

		return self.__dict__[attr]  # pragma: nocover

	def __setattr__(self, attr, value):
		self.__dict__[attr] = value

	def __delattr__(self, attr):
		if attr not in self.__dict__:
			raise AttributeError(attr)

		del self.__dict__[attr]

	def __getitem__(self, key):
		if key in self.__dict__:
			return self.__dict__[key]

		if hasattr(self.__class__, '__missing__'):
			return self.__class__.__missing__(self, key)

		raise KeyError(key)

	def __setitem__(self, key, value):
		self.__dict__[key] = value

	def __delitem__(self, key):
		del self.__dict__[key]

	def __iter__(self):
		return iter(self.__dict__)

	def __len__(self):
		return len(self.__dict__)

	def __repr__(self, repr_dict=None):
		repr_dict = repr_dict if repr_dict is not None else self.__dict__
		return f"<{self.__class__.__name__}({pprintpp.pformat(repr_dict)})>"

	@classmethod
	def from_mapping(cls, mapping):
		return cls(**mapping)

	def items(self):
		return _ItemsView(self)

	def keys(self):
		return _KeysView(self)

	def values(self):
		return _ValuesView(self)


class LabelList(UserList):
	item_label = ('item', 'items')

	def __repr__(self):
		item_label = self.item_label[1] if len(self.data) > 1 else self.item_label[0]
		return f"<{self.__class__.__name__} ({len(self)} {item_label})>"

	@property
	def items(self):
		return self.data
