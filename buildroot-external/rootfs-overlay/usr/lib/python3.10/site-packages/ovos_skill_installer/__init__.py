#!/usr/bin/env python3
import hashlib
import os
import tarfile
from os.path import join, basename, isdir, isfile, exists
from tempfile import mkstemp
import zipfile
import requests
import shutil
from os import makedirs, listdir


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


def download(url, file=None, session=None):
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

    if isinstance(file, str):
        file = open(file, 'wb')
    try:
        if session:
            content = session.get(url).content
        else:
            content = requests.get(url).content
        if file:
            file.write(content)
        else:
            return content
    finally:
        if file:
            file.close()


def download_extract_tar(tar_url, folder, tar_filename='',
                         skill_folder_name=None, session=None):
    """
    Download and extract the tar at the url to the given folder

    Args:
        tar_url (str): URL of tar file to download
        folder (str): Location of parent directory to extract to. Doesn't have to exist
        tar_filename (str): Location to download tar. Default is to a temp file
        skill_folder_name (str): rename extracted skill folder to this
    """
    try:
        makedirs(folder)
    except OSError:
        if not isdir(folder):
            raise
    if not tar_filename:
        fd, tar_filename = mkstemp('.tar.gz')
        download(tar_url, os.fdopen(fd, 'wb'), session=session)
    else:
        download(tar_url, tar_filename, session=session)

    with tarfile.open(tar_filename) as tar:
        tar.extractall(path=folder)

    if skill_folder_name:
        with tarfile.open(tar_filename) as tar:
            for p in tar.getnames():
                original_folder = p.split("/")[0]
                break
        original_folder = join(folder, original_folder)
        final_folder = join(folder, skill_folder_name)
        shutil.move(original_folder, final_folder)


def download_extract_zip(zip_url, folder, zip_filename="",
                         skill_folder_name=None, session=None):
    """
   Download and extract the zip at the url to the given folder

   Args:
       zip_url (str): URL of zip file to download
       folder (str): Location of parent directory to extract to. Doesn't have to exist
       zip_filename (str): Location to download zip. Default is to a temp file
       skill_folder_name (str): rename extracted skill folder to this
   """
    try:
        makedirs(folder)
    except OSError:
        if not isdir(folder):
            raise
    if not zip_filename:
        fd, zip_filename = mkstemp('.tar.gz')
        download(zip_url, os.fdopen(fd, 'wb'), session=session)
    else:
        download(zip_url, zip_filename, session=session)

    with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
        zip_ref.extractall(folder)

    if skill_folder_name:
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            for p in zip_ref.namelist():
                original_folder = p.split("/")[0]
                break

        original_folder = join(folder, original_folder)
        final_folder = join(folder, skill_folder_name)
        shutil.move(original_folder, final_folder)


def get_remote_md5(md5_url, file_url=None, data_file=None, session=None):
    try:
        if requests.get(md5_url).status_code == 200:
            return download(md5_url, session=session).decode('utf-8').split(' ')[0], None
    except Exception as e:
        pass
    if file_url:
        # print("md5 url not available, need to download first!")
        if not data_file:
            if file_url.endswith(".tar.gz"):
                ext = ".tar.gz"
            else:
                ext = basename(file_url).split(".")[-1]
            fd, data_file = mkstemp(ext)
        download(file_url, data_file, session=session)
        return calc_md5(data_file), data_file
    else:
        raise ValueError('Invalid MD5 url: ' + md5_url)


def install_skill(url, folder, filename=None, md5_url='{url}.md5',
                  skill_folder_name=None, session=None, ignore_md5=False):
    """
    Install or update a tar/zip package

    Args:
        url (str): URL of package to download
        folder (str): Location to extract to. Will be created if doesn't exist
        filename (str): filename of downloaded tar/zip file
        md5_url (str): URL of md5 to use to check for updates
        skill_folder_name (str): rename extracted skill folder to this
        session (requests.Session): a session to be reutilized
        ignore_md5 (bool): ignore md5 hash and just replace existing skill

    Returns:
        bool: Whether the package was updated
    """
    if "{url}" in md5_url:
        md5_url = md5_url.format(url=url)

    if url.endswith(".zip") or "zipball" in url and "github" in url:
        return install_skill_from_zip(url, folder, filename, md5_url,
                                      skill_folder_name, session=session)
    else:
        return install_skill_from_tar(url, folder, filename, md5_url,
                                      skill_folder_name, session=session)


def install_skill_from_tar(tar_url, folder, filename=None,
                           md5_url='{tar_url}.md5', skill_folder_name=None,
                           session=None, ignore_md5=False):
    """
    Install or update a tar package

    Args:
        tar_url (str): URL of package to download
        folder (str): Location to extract tar. Will be created if doesn't exist
        filename (str): filename of downloaded tar file
        md5_url (str): URL of md5 to use to check for updates
        skill_folder_name (str): rename extracted skill folder to this
        session (requests.Session): a session to be reutilized
        ignore_md5 (bool): ignore md5 hash and just replace existing skill

    Returns:
        bool: Whether the package was updated
    """
    if "{tar_url}" in md5_url:
        md5_url = md5_url.format(tar_url=tar_url)

    filename = filename or basename(tar_url)
    data_file = join(folder, filename)
    if skill_folder_name:
        final_folder = join(folder, skill_folder_name)

    if ignore_md5:
        downloaded = False
        need_to_download = True
    else:
        remote_md5, downloaded = get_remote_md5(md5_url, tar_url,
                                                session=session)
        if skill_folder_name:
            need_to_download = not exists(final_folder)
        else:
            need_to_download = remote_md5 != calc_md5(data_file)

    if need_to_download:
        original_folder = None
        # remove old files
        if isfile(data_file):
            # check tar default folder
            try:
                with tarfile.open(data_file) as tar:
                    for p in tar.getnames():
                        shutil.rmtree(join(folder, p), ignore_errors=True)
            except (OSError, EOFError):
                pass

        # check and delete renamed folder if requested
        if (ignore_md5 or skill_folder_name) and isdir(final_folder):
            shutil.rmtree(final_folder, ignore_errors=True)

        # extract already downloaded
        if downloaded:
            with tarfile.open(downloaded) as tar:
                tar.extractall(path=folder)
                for p in tar.getnames():
                    original_folder = p.split("/")[0]
                    break

            # move .tar.gz file for md5 calculations
            shutil.move(downloaded, data_file)

            # move extracted to requested final dir
            if skill_folder_name and original_folder:
                shutil.move(join(folder, original_folder), final_folder)

        # download and extract
        else:
            download_extract_tar(tar_url, folder, data_file,
                                 skill_folder_name=skill_folder_name,
                                 session=session)
        if not ignore_md5:
            local_md5 = calc_md5(data_file)
            if remote_md5 != local_md5:
                raise ValueError('MD5 url does not match tar: ' + md5_url)
        return True
    return False


def install_skill_from_zip(zip_url, folder, filename=None,
                           md5_url='{zip_url}.md5', skill_folder_name=None,
                           session=None, ignore_md5=False):
    """
    Install or update a zip package

    Args:
        zip_url (str): URL of package to download
        folder (str): Location to extract tar. Will be created if doesn't exist
        filename (str): filename of downloaded zip file
        md5_url (str): URL of md5 to use to check for updates
        skill_folder_name (str): rename extracted skill folder to this
        session (requests.Session): a session to be reutilized
        ignore_md5 (bool): ignore md5 hash calculations

    Returns:
        bool: Whether the package was updated
    """
    if "{zip_url}" in md5_url:
        md5_url = md5_url.format(zip_url=zip_url)

    filename = filename or basename(zip_url)
    data_file = join(folder, filename)
    if skill_folder_name:
        final_folder = join(folder, skill_folder_name)

    if ignore_md5:
        downloaded = False
        need_to_download = True
    else:
        remote_md5, downloaded = get_remote_md5(md5_url, zip_url, session=session)
        if skill_folder_name:
            need_to_download = not exists(final_folder)
        else:
            need_to_download = remote_md5 != calc_md5(data_file)

    if need_to_download:
        original_folder = None
        # remove old files
        if isfile(data_file):
            with zipfile.ZipFile(data_file, 'r') as zip_ref:
                for p in zip_ref.namelist():
                    shutil.rmtree(join(folder, p), ignore_errors=True)

        # check and delete renamed folder if requested
        if (ignore_md5 or skill_folder_name) and isdir(final_folder):
            shutil.rmtree(final_folder, ignore_errors=True)

        # extract already downloaded
        if downloaded:
            with zipfile.ZipFile(downloaded, 'r') as zip_ref:
                zip_ref.extractall(folder)
                for p in zip_ref.namelist():
                    original_folder = p.split("/")[0]
                    break

            # move .zip file for md5 calculations
            shutil.move(downloaded, data_file)

            # move extracted to requested final dir
            if skill_folder_name and original_folder:
                shutil.move(join(folder, original_folder), final_folder)

        # download and extract
        else:
            download_extract_zip(zip_url, folder, data_file,
                                 skill_folder_name=skill_folder_name,
                                 session=session)

        if not ignore_md5:
            local_md5 = calc_md5(data_file)
            if remote_md5 != local_md5:
                raise ValueError('MD5 url does not match zip: ' + md5_url)
        return True
    return False
