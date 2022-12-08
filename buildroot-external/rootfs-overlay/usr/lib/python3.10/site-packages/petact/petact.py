#!/usr/bin/env python3
import hashlib
import os
import tarfile
from argparse import ArgumentParser
from os.path import join, basename, isdir, isfile
from tempfile import mkstemp

from os import makedirs

from urllib.error import URLError


def calc_md5(filename):
    """
    Computes the md5 sum of the given filename.

    Args:
        filename (str): Filename to calculate the sum of
    Returns:
        str: md5 sum hex string
    """
    if not isfile(filename):
        return None
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def download(url, file=None):
    """
    Pass file as a filename, open file object, or None to return the request bytes

    Args:
        url (str): URL of file to download
        file (Union[str, io, None]): One of the following:
             - Filename of output file
             - File opened in binary write mode
             - None: Return raw bytes instead

    Returns:
        Union[bytes, None]: Bytes of file if file is None
    """
    import urllib.request
    import shutil
    if isinstance(file, str):
        file = open(file, 'wb')
    try:
        with urllib.request.urlopen(url) as response:
            if file:
                shutil.copyfileobj(response, file)
            else:
                return response.read()
    finally:
        if file:
            file.close()


def download_extract_tar(tar_url, folder, tar_filename=''):
    """
    Download and extract the tar at the url to the given folder

    Args:
        tar_url (str): URL of tar file to download
        folder (str): Location of parent directory to extract to. Doesn't have to exist
        tar_filename (str): Location to download tar. Default is to a temp file
    """
    try:
        makedirs(folder)
    except OSError:
        if not isdir(folder):
            raise
    data_file = tar_filename
    if not data_file:
        fd, data_file = mkstemp('.tar.gz')
        download(tar_url, os.fdopen(fd, 'wb'))
    else:
        download(tar_url, data_file)

    with tarfile.open(data_file) as tar:
        tar.extractall(path=folder)


def install_package(tar_url, folder, md5_url='{tar_url}.md5',
                    on_download=lambda: None, on_complete=lambda: None):
    """
    Install or update a tar package that has an md5

    Args:
        tar_url (str): URL of package to download
        folder (str): Location to extract tar. Will be created if doesn't exist
        md5_url (str): URL of md5 to use to check for updates
        on_download (Callable): Function that gets called when downloading a new update
        on_complete (Callable): Function that gets called when a new download is complete

    Returns:
        bool: Whether the package was updated
    """
    data_file = join(folder, basename(tar_url))

    md5_url = md5_url.format(tar_url=tar_url)
    try:
        remote_md5 = download(md5_url).decode('utf-8').split(' ')[0]
    except (UnicodeDecodeError, URLError):
        raise ValueError('Invalid MD5 url: ' + md5_url)
    if remote_md5 != calc_md5(data_file):
        on_download()
        if isfile(data_file):
            try:
                with tarfile.open(data_file) as tar:
                    for i in reversed(list(tar)):
                        try:
                            os.remove(join(folder, i.path))
                        except OSError:
                            pass
            except (OSError, EOFError):
                pass

        download_extract_tar(tar_url, folder, data_file)
        on_complete()
        if remote_md5 != calc_md5(data_file):
            raise ValueError('MD5 url does not match tar: ' + md5_url)
        return True
    return False


def main():
    parser = ArgumentParser()
    parser.add_argument('tar_url')
    parser.add_argument('folder')
    parser.add_argument('-m', '--md5-url', default='{tar_url}.md5')
    args = parser.parse_args()
    install_package(args.tar_url, args.folder, args.md5_url,
                    on_download=lambda: print('Updating...'),
                    on_complete=lambda: print('Update complete.'))


if __name__ == '__main__':
    main()
