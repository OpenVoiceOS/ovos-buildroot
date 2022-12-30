# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import json
import os.path

from enum import Enum
from urllib.parse import urlparse
from neon_utils.logger import LOG


class CredentialEnvVar(Enum):
    """
    Mapping of service to well-known envvars
    """
    GITHUB = ("GH_TOKEN", "GITHUB_TOKEN")
    AWS_ID = ("AWS_ACCESS_KEY_ID",)
    AWS_SECRET = ("AWS_SECRET_ACCESS_KEY",)
    GOOGLE_CREDENTIALS = ("GOOGLE_APPLICATION_CREDENTIALS",)  # File ref
    WOLFRAM = ("WOLFRAM_APP_ID",)  # Neon Defined
    ALPHA_VANTAGE = ("ALPHA_VANTAGE_KEY",)  # Neon Defined
    OPEN_WEATHER_MAP = ("OWM_KEY",)  # Neon Defined


class CredentialNotFoundError(FileNotFoundError):
    """Credential not found in environ or requested file paths"""


def find_generic_keyfile(base_path: str, filename: str) -> str:
    """
    Locates a generic text keyfile
    Args:
        base_path: Base directory to check in addition to XDG directories
        (default ~/)
        filename: File basename to read
    Returns:
        str contents of located file
    """
    path_to_check = os.path.expanduser(base_path)
    paths_to_check = (path_to_check,
                      os.path.join(path_to_check, filename),
                      os.path.expanduser(f"~/.local/share/neon/{filename}"))
    for path in paths_to_check:
        if os.path.isfile(path):
            with open(path, "r") as f:
                credential = f.read().strip()
            return credential
    raise FileNotFoundError(f"No credentials found in default locations or "
                            f"path: {path_to_check}")


def find_environment_key(service: CredentialEnvVar):
    """
    Locate a credential in environment variables
    :param service: Credential to locate
    """
    for param in service.value:
        if os.getenv(param):
            return os.getenv(param)
    return None


def find_neon_git_token(base_path: str = "~/") -> str:
    """
    Searches environment variables and standard locations for a text file with
    a Github token.
    Args:
        base_path: Base directory to check in addition to XDG directories
        (default ~/)
    Returns:
        Github token string
    """
    env_token = find_environment_key(CredentialEnvVar.GITHUB)
    if env_token:
        return env_token
    try:
        return find_generic_keyfile(base_path, "token.txt")
    except FileNotFoundError:
        pass
    try:
        return find_generic_keyfile(base_path, "git_token.txt")
    except FileNotFoundError:
        pass

    raise CredentialNotFoundError("Could not locate github credentials")


def find_neon_aws_keys(base_path: str = "~/") -> dict:
    """
    Searches environment variables and standard locations for AWS credentials
    Args:
        base_path: Base directory to check in addition to XDG directories
        (default ~/)
    Returns:
        dict containing 'aws_access_key_id' and 'aws_secret_access_key'
    """
    env_aws_id = find_environment_key(CredentialEnvVar.AWS_ID)
    env_aws_key = find_environment_key(CredentialEnvVar.AWS_SECRET)
    if env_aws_id and env_aws_key:
        return {"aws_access_key_id": env_aws_id,
                "aws_secret_access_key": env_aws_key}

    try:
        csv_contents = find_generic_keyfile(base_path, "accessKeys.csv")
    except FileNotFoundError:
        csv_contents = None
    if csv_contents:
        try:
            aws_id, aws_key = csv_contents.split('\n')[1].split(',', 1)
            return {"aws_access_key_id": aws_id,
                    "aws_secret_access_key": aws_key}
        except Exception as e:
            LOG.error(e)

    try:
        json_contents = find_generic_keyfile(base_path, "aws.json")
    except FileNotFoundError:
        json_contents = None
    if json_contents:
        try:
            return json.loads(json_contents)
        except Exception as e:
            LOG.error(e)

    try:
        file_contents = find_generic_keyfile("~/.aws", "credentials")
    except FileNotFoundError:
        file_contents = None
    if file_contents:
        aws_id, aws_key = None, None
        for line in file_contents.split("\n"):
            if line.startswith("aws_access_key_id"):
                aws_id = line.split("=", 1)[1].strip()
            elif line.startswith("aws_secret_access_key"):
                aws_key = line.split("=", 1)[1].strip()
        if aws_id and aws_key:
            return {"aws_access_key_id": aws_id,
                    "aws_secret_access_key": aws_key}

    raise CredentialNotFoundError(f"No aws credentials found in default "
                                  f"locations or path: {base_path}")


def find_neon_google_keys(base_path: str = "~/") -> dict:
    """
    Locates google json credentials and returns the parsed
    credentials as a dict
    Args:
        base_path: Base directory to check in addition to XDG directories
        (default ~/)
    Returns:
        dict Google json credential
    """
    env_cred_file = find_environment_key(CredentialEnvVar.GOOGLE_CREDENTIALS)
    if env_cred_file and os.path.isfile(env_cred_file):
        try:
            with open(env_cred_file, 'r') as f:
                credential = json.load(f)
            return credential
        except Exception as e:
            LOG.error(f"Invalid google credential found at: {env_cred_file}")
            LOG.error(e)
    try:
        cred_str = find_generic_keyfile(base_path, "google.json")
        credential = json.loads(cred_str)
        return credential
    except Exception as e:
        LOG.error(e)
    raise CredentialNotFoundError(f"No google credentials found in default "
                                  f"locations or path: {base_path}")


def find_neon_wolfram_key(base_path: str = "~/") -> str:
    """
    Locates Wolfram|Alpha API key
    Args:
        base_path: Base directory to check in addition to XDG directories
         (default ~/)
    Returns:
        str Wolfram|Alpha API key
    """
    return find_environment_key(CredentialEnvVar.WOLFRAM) or \
        find_generic_keyfile(base_path, "wolfram.txt")


def find_neon_alpha_vantage_key(base_path: str = "~/") -> str:
    """
    Locates Alpha Vantage API key
    Args:
        base_path: Base directory to check in addition to XDG directories
         (default ~/)
    Returns:
        str Alpha Vantage API key
    """
    return find_environment_key(CredentialEnvVar.ALPHA_VANTAGE) or \
        find_generic_keyfile(base_path, "alpha_vantage.txt")


def find_neon_owm_key(base_path: str = "~/") -> str:
    """
    Locates Open Weather Map key
    Args:
        base_path: Base directory to check in addition to XDG directories
         (default ~/)
    Returns:
        str Open Weather Map API key
    """
    return find_environment_key(CredentialEnvVar.OPEN_WEATHER_MAP) or \
        find_generic_keyfile(base_path, "owm.txt")


def repo_is_neon(repo_url: str) -> bool:
    """
    Determines if the specified repository url is part of the NeonGeckoCom
    org on github
    Args:
        repo_url: string url to check
    Returns:
        True if the repository URL is known to be accessible using a neon
        auth key
    """
    url = urlparse(repo_url)
    if not url.scheme or not url.netloc:
        raise ValueError(f"{repo_url} is not a valid url")
    if any([x for x in ("github.com", "githubusercontent.com")
            if x in url.netloc]):
        try:
            author = url.path.split('/')[1]
        except IndexError:
            raise ValueError(f"{repo_url} is not a valid github url")
        if author.lower() == "neongeckocom":
            return True
        elif author.lower().startswith("neon"):
            # TODO: Get token and scrape org? DM
            LOG.info(f"Assuming repository uses Neon auth: {repo_url}")
            return True
    return False


def build_new_auth_config(key_path: str = "~/") -> dict:
    """
    Constructs a dict of authentication key data by locating credential files
        in the specified path
    :param key_path: path to locate key files
        (default locations checked in addition)
    :return: dict of located authentication keys
    """
    key_path = key_path or "~/"
    auth_config = {"github": {"token": find_neon_git_token},
                   "amazon": find_neon_aws_keys,
                   "wolfram": {"app_id": find_neon_wolfram_key},
                   "google": find_neon_google_keys,
                   "alpha_vantage": {"api_key": find_neon_alpha_vantage_key},
                   "owm": {"api_key": find_neon_owm_key}
                   }
    for cred in auth_config:
        try:
            if isinstance(auth_config[cred], dict):
                for real_cred in auth_config[cred]:
                    auth_config[cred][real_cred] = \
                        auth_config[cred][real_cred](key_path)
            else:
                auth_config[cred] = auth_config[cred](key_path)
        except FileNotFoundError:
            auth_config[cred] = dict()
            LOG.error(f"No credentials found for: {cred}")

    return auth_config
