__all__ = [
	'FILEPATH_CHARACTER_REPLACEMENTS',
]


FILEPATH_CHARACTER_REPLACEMENTS = {
	'\\': '-',
	'/': ',',
	':': '-',
	'*': 'x',
	'<': '[',
	'>': ']',
	'|': '!',
	'?': '',
	'"': "''",
}
"""dict: Mapping of invalid filepath characters with appropriate replacements."""
