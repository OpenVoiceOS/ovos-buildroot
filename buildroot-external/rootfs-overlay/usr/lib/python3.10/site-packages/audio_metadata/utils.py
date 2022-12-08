import os
import struct
from codecs import (
	BOM_UTF16_BE,
	BOM_UTF16_LE,
)
from functools import reduce

from tbm_utils import datareader
from tbm_utils import humanize_duration as tbm_humanize_duration


def apply_unsynchronization(data):
	"""Apply ID3v2 unsynchronization scheme to data."""

	sync_index = data.find(b'\xFF')
	if sync_index == -1:
		return data

	data = bytearray(data)

	d = bytearray()
	while sync_index != -1:
		d += data[:sync_index + 1]

		b = data[sync_index + 1 : sync_index + 2]
		if b >= b'\xE0':
			d += b'\x00'
			d += b
		elif b == b'\x00':
			d += b'\x00\x00'
		else:
			d += b

		data = data[sync_index + 2:]

		sync_index = data.find(b'\xFF')

	d += data

	return bytes(d)


def remove_unsynchronization(data):
	"""Remove ID3v2 unsynchronization scheme from data."""

	sync_index = data.find(b'\xFF')
	if sync_index == -1:
		return data

	data = bytearray(data)

	d = bytearray()
	while sync_index != -1:
		d += data[:sync_index]

		if data[sync_index + 1 : sync_index + 3] == b'\x00\x00':
			d += b'\xFF\x00'
			data = data[sync_index + 3:]
		elif data[sync_index + 1 : sync_index + 2] == b'\x00':
			d += b'\xFF'
			data = data[sync_index + 2:]
		else:
			d += b'\xFF'
			data = data[sync_index + 1:]

		sync_index = data.find(b'\xFF')

	d += data

	return bytes(d)


def decode_synchsafe_int(data, per_byte):
	"""Decode synchsafe integers from ID3v2 tags."""

	i = reduce(lambda value, element: (value << per_byte) + element, data, 0)

	if i > 2 ** (per_byte * 4) - 1:
		raise ValueError(
			f"{data} is too large to be a synchsafe "
			f"integer with {per_byte} bits per byte."
		)

	return i


def encode_synchsafe_int(i, per_byte):
	"""Encode synchsafe integers for ID3v2 tags."""

	if i > 2 ** (per_byte * 4) - 1:
		raise ValueError(
			f"{i} is too large to be represented by a synchsafe "
			f"integer with {per_byte} bits per byte."
		)

	v = 0
	mask = 0x7F

	value = i
	while ((mask ^ 0x7FFFFFFF) > 0):
		v = value & ~mask
		v = v << (8 - per_byte)
		v = v | (value & mask)
		mask = ((mask + 1) << 8) - 1
		value = v

	return value.to_bytes(4, byteorder='big')


def decode_bytestring(b, encoding='iso-8859-1'):
	"""Decode ID3v2 frame data using given encoding."""

	if not b:
		return ''

	if encoding.startswith('utf-16'):
		if len(b) % 2 and b[-1:] == b'\x00':
			b = b[:-1]

		if b.startswith((BOM_UTF16_BE, BOM_UTF16_LE)):  # pragma: nobranch
			b = b[2:]

	return b.decode(encoding).rstrip('\x00')


def determine_encoding(b):
	"""Determine encoding of ID3v2 frame data."""

	first = b[0:1]

	if first == b'\x00':
		encoding = 'iso-8859-1'
	elif first == b'\x01':
		encoding = 'utf-16-be' if b[1:3] == BOM_UTF16_BE else 'utf-16-le'
	elif first == b'\x02':
		encoding = 'utf-16-be'
	elif first == b'\x03':
		encoding = 'utf-8'
	else:
		encoding = 'iso-8859-1'

	return encoding


def split_encoded(data, encoding, max_split=None):
	"""Split ID3v2 frame data according to encoding."""

	remainder = data

	values = []
	num_split = 0
	while True:
		try:
			if encoding in ['iso-8859-1', 'utf-8']:
				head, tail = remainder.split(b'\x00', 1)
			else:
				if len(remainder) % 2 != 0:
					remainder += b'\x00'

				head, tail = remainder.split(b'\x00\x00', 1)

				if len(head) % 2 != 0:
					head, tail = remainder.split(b'\x00\x00\x00', 1)
					head += b'\x00'
		except ValueError:
			if remainder:
				values.append(remainder)
			break
		else:
			values.append(head)
			remainder = tail

			num_split += 1
			if (
				max_split
				and num_split >= max_split
			):
				values.append(tail)
				break

	return values


@datareader
def get_image_size(data):
	"""Determine dimensions from image file data."""

	b = data.read(56)
	size = len(b)

	width = height = 0
	if size >= 10 and b[:6] in [b'GIF87a', b'GIF89a']:
		width, height = struct.unpack('<hh', b[6:10])
	elif size >= 24 and b.startswith(b'\x89PNG') and b[12:16] == b'IHDR':
		width, height = struct.unpack('>LL', b[16:24])
	elif size >= 2 and b.startswith(b'\xff\xd8'):
		data.seek(0)

		size = 2
		ftype = 0
		while not 0xC0 <= ftype <= 0xCF or ftype in [0xC4, 0xC8, 0xCC]:
			data.seek(size, os.SEEK_CUR)
			while True:
				b = data.read(1)
				if b != b'\xff':
					break

			ftype = ord(b)
			size = struct.unpack('>H', data.read(2))[0] - 2

		data.seek(1, os.SEEK_CUR)
		height, width = struct.unpack('>HH', data.read(4))
	elif size >= 12 and b.startswith(b'\x00\x00\x00\x0cjP'):
		height, width = struct.unpack('>LL', b[48:])
	elif b.startswith(b'BM'):
		width, height = struct.unpack('<II', b[18:26])
	else:
		raise ValueError(f"Unsupported image file format.")

	return width, height


def humanize_bitrate(bitrate):
	"""Humanize bitrate from integer."""

	if bitrate is not None:
		for divisor, symbol in [(1000 ** 1, 'Kbps'), (1, 'bps')]:
			if bitrate >= divisor:
				break

		return f'{round(bitrate / divisor)} {symbol}'


def humanize_duration(duration):
	"""Humanize duration from integer."""

	if duration is not None:
		return tbm_humanize_duration(duration)


def humanize_sample_rate(sample_rate):
	"""Humanize sample rate from integer."""

	if sample_rate is not None:
		for divisor, symbol in [(1000 ** 1, 'KHz'), (1, 'Hz')]:
			if sample_rate >= divisor:
				break

		value = sample_rate / divisor

		return f'{value if value.is_integer() else value:.1f} {symbol}'
