__all__ = [
	'humanize_bitrate',
	'humanize_duration',
	'humanize_filesize',
	'humanize_sample_rate'
]


SYMBOLS = {
	'binary': [
		(1024 ** 8, 'Yi'),
		(1024 ** 7, 'Zi'),
		(1024 ** 6, 'Ei'),
		(1024 ** 5, 'Pi'),
		(1024 ** 4, 'Ti'),
		(1024 ** 3, 'Gi'),
		(1024 ** 2, 'Mi'),
		(1024 ** 1, 'Ki'),
		(1, '')
	],
	'decimal': [
		(1000 ** 8, 'Y'),
		(1000 ** 7, 'Z'),
		(1000 ** 6, 'E'),
		(1000 ** 5, 'P'),
		(1000 ** 4, 'T'),
		(1000 ** 3, 'G'),
		(1000 ** 2, 'M'),
		(1000 ** 1, 'K'),
		(1, '')
	]
}


def _get_symbol(value, system):
	for divisor, symbol in SYMBOLS[system]:
		if value >= divisor:
			break

	return divisor, symbol


def humanize_bitrate(bitrate, *, system='decimal'):
	divisor, symbol = _get_symbol(bitrate, system)

	return f'{round(bitrate / divisor)} {symbol}bps'


def humanize_duration(duration):
	if duration // 3600:
		hours = int(duration // 3600)
		minutes = int(duration % 3600 // 60)
		seconds = round(duration % 3600 % 60)

		return f'{hours:02d}:{minutes:02d}:{seconds:02d}'
	elif duration // 60:
		minutes = int(duration // 60)
		seconds = round(duration % 60)

		return f'{minutes:02d}:{seconds:02d}'
	else:
		return f'00:{round(duration):02d}'


def humanize_filesize(filesize, *, precision=0, system='binary', **kwargs):
	divisor, symbol = _get_symbol(filesize, system)

	return f'{filesize / divisor:.{precision}f} {symbol}B'


def humanize_sample_rate(sample_rate, *, system='decimal'):
	divisor, symbol = _get_symbol(sample_rate, system)
	value = sample_rate / divisor

	if value.is_integer():
		humanized = f'{int(value)} {symbol}Hz'
	else:
		humanized = f'{value:.1f} {symbol}Hz'

	return humanized
