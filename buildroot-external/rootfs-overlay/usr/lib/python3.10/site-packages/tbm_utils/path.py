__all__ = [
	'UNIX_PATH_RE',
	'convert_unix_path'
]

import re
from pathlib import Path


UNIX_PATH_RE = re.compile(r'(/(cygdrive/)?)(.*)')
"""Regex pattern matching UNIX-style filepaths."""


def convert_unix_path(filepath):
	"""Convert Unix filepath string from Unix to Windows format.

	Parameters:
		filepath (str, os.PathLike, Path): A filepath string.

	Returns:
		Path: A Windows path object.

	Raises:
		FileNotFoundError
		subprocess.CalledProcessError
	"""

	match = UNIX_PATH_RE.match(str(filepath))
	if not match:
		return Path(filepath.replace('/', r'\\'))

	parts = match.group(3).split('/')
	parts[0] = f"{parts[0].upper()}:/"

	return Path(*parts)
