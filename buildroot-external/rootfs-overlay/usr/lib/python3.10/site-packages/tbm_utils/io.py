__all__ = [
	'DataReader',
	'DataWriter',
]

import os
from io import (
	DEFAULT_BUFFER_SIZE,
	BufferedRandom,
	BufferedReader,
	BufferedWriter,
	BytesIO,
	FileIO,
)


class DataReader(BufferedReader):
	"""A buffered reader wrapper.

	It includes support for filepaths, file-like objects, and bytes-like objects.

	Parameters:
		data (DataReader, BufferedIOBase, os.PathLike, str, bytes, bytearray, memoryview):
			The object to provide the :class:`BufferedReader` interface for.
		buffer_size(int): The size of the internal buffer. (Default: io.DEFAULT_BUFFER_SIZE)
	"""

	def __init__(
		self,
		data,
		buffer_size=DEFAULT_BUFFER_SIZE,
	):
		if isinstance(data, (BufferedReader, BufferedRandom)):
			if isinstance(data.raw, FileIO):
				data = FileIO(data.name, 'rb')
			else:
				data = BytesIO(data.read())
		elif isinstance(data, BytesIO):
			data = BytesIO(data.getvalue())
		elif isinstance(data, FileIO):
			data = FileIO(data.name, 'rb')
		elif isinstance(data, (os.PathLike, str)):
			data = FileIO(data, 'rb')
		elif isinstance(data, (bytearray, bytes, memoryview)):
			data = BytesIO(data)

		super().__init__(data, buffer_size=buffer_size)

		self.accumulator = 0
		self.bit_count = 0

	def peek(self, size=DEFAULT_BUFFER_SIZE):
		if size > DEFAULT_BUFFER_SIZE:
			size = DEFAULT_BUFFER_SIZE

		peeked = super().peek(size)[:size]

		if len(peeked) < size:
			peeked = self.read(size)
			self.seek(-len(peeked), os.SEEK_CUR)

		return peeked

	def read(self, size=-1):
		self.accumulator = 0
		self.bit_count = 0

		return super().read(size)

	# From https://rosettacode.org/wiki/Bitwise_IO#Python
	def _readbit(self):
		if not self.bit_count:
			a = self.read(1)

			if a:  # pragma: nobranch
				self.accumulator = ord(a)

			self.bit_count = 8

		rv = (self.accumulator & (1 << self.bit_count - 1)) >> self.bit_count - 1

		self.bit_count -= 1

		return rv

	def readbits(self, n):
		v = 0
		while n > 0:
			v = (v << 1) | self._readbit()
			n -= 1

		return v

	def find(self, sub, start=None, end=None):
		try:
			return self.index(sub, start, end)
		except ValueError:
			return -1

	def rfind(self, sub, start=None, end=None):
		try:
			return self.rindex(sub, start, end)
		except ValueError:
			return -1

	def index(self, sub, start=None, end=None):
		orig_position = self.tell()

		if start is None:
			start = 0

		if end is None:
			self.seek(0, os.SEEK_END)
			end = self.tell()

		self.seek(start, os.SEEK_SET)

		while self.tell() < end:
			peeked = self.peek()
			try:
				i = peeked.index(sub)
			except ValueError:
				self.seek(len(peeked), os.SEEK_CUR)
			else:
				index = i + self.tell()
				self.seek(orig_position, os.SEEK_SET)
				break
		else:
			self.seek(orig_position, os.SEEK_SET)

			raise ValueError("Subsequence not found.")

		return index

	def rindex(self, sub, start=None, end=None):
		orig_position = self.tell()

		if start is None:
			start = 0

		if end is None:
			self.seek(0, os.SEEK_END)
			end = self.tell()

		if end < DEFAULT_BUFFER_SIZE:
			step = end
			self.seek(0, os.SEEK_SET)
		else:
			step = DEFAULT_BUFFER_SIZE
			self.seek(-step, os.SEEK_END)

		read = 0
		while read < end:
			peeked = self.peek(step)
			read += len(peeked)

			try:
				i = peeked.rindex(sub)
			except ValueError:
				self.seek(-len(peeked), os.SEEK_CUR)
			else:
				index = i + self.tell()
				self.seek(orig_position, os.SEEK_SET)
				break
		else:
			self.seek(orig_position, os.SEEK_SET)

			raise ValueError("Subsequence not found.")

		return index

	def seek_first(self, sub):
		"""Seek to the first index of a subsequence in data."""

		self.seek(0, os.SEEK_SET)

		try:
			index = self.index(sub, start=0)
		except ValueError:
			raise
		else:
			self.seek(index, os.SEEK_SET)

	def seek_last(self, sub):
		"""Seek to the last index of a subsequence in data."""

		try:
			index = self.rindex(sub)
		except ValueError:
			raise
		else:
			self.seek(index, os.SEEK_SET)

	def seek_next(self, sub):
		"""Seek to the next index of a subsequence in data."""

		try:
			index = self.index(sub, self.tell())
		except ValueError:
			raise
		else:
			self.seek(index, os.SEEK_SET)


class DataWriter(BufferedWriter):
	"""A buffered writer wrapper.

	It includes support for filepaths, file-like objects, and bytes-like objects.

	Parameters:
		data (DataReader, BufferedIOBase, os.PathLike, str, bytes, bytearray, memoryview):
			The object to provide the :class:`BufferedWriter` interface for.
		buffer_size(int): The size of the internal buffer. (Default: io.DEFAULT_BUFFER_SIZE)
	"""

	def __init__(
		self,
		data,
		buffer_size=DEFAULT_BUFFER_SIZE,
	):
		if isinstance(data, (BufferedWriter, BufferedRandom)):
			if isinstance(data.raw, FileIO):
				data = FileIO(data.name, 'wb')
			else:
				data = BytesIO(data.read())
		elif isinstance(data, BytesIO):
			data = BytesIO(data.getvalue())
		elif isinstance(data, FileIO):
			data = FileIO(data.name, 'wb')
		elif isinstance(data, (os.PathLike, str)):
			data = FileIO(data, 'wb')
		elif isinstance(data, (bytearray, bytes, memoryview)):
			data = BytesIO(data)

		super().__init__(data, buffer_size=buffer_size)
