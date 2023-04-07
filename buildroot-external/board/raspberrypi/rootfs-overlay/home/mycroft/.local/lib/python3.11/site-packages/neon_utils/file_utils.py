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

import glob
import os
import base64
import wave

from tempfile import mkstemp

from typing import Optional, List
from ovos_utils.signal import ensure_directory_exists

from neon_utils.logger import LOG

try:
    from pydub import AudioSegment
except ImportError:
    LOG.warning("pydub not available, pip install neon-utils[audio]")
    AudioSegment = None


def encode_file_to_base64_string(path: str) -> str:
    """
    Encodes a file to a base64 string (useful for passing file data over a messagebus)
    :param path: Path to file to be encoded
    :return: encoded string
    """
    if not isinstance(path, str):
        raise TypeError
    path = os.path.expanduser(path)
    if not os.path.isfile(path):
        LOG.error(f"File Not Found: {path}")
        raise FileNotFoundError
    with open(path, "rb") as file_in:
        encoded = base64.b64encode(file_in.read()).decode("utf-8")
    return encoded


def decode_base64_string_to_file(encoded_string: str, output_path: str) -> str:
    """
    Writes out a base64 string to a file object at the specified path
    :param encoded_string: Base64 encoded string
    :param output_path: Path to file to write (throws exception if file exists)
    :return: Path to output file
    """
    if not isinstance(output_path, str):
        raise TypeError
    output_path = os.path.expanduser(output_path)
    if os.path.isfile(output_path):
        LOG.error(f"File already exists: {output_path}")
        raise FileExistsError
    ensure_directory_exists(os.path.dirname(output_path))
    with open(output_path, "wb+") as file_out:
        byte_data = base64.b64decode(encoded_string.encode("utf-8"))
        file_out.write(byte_data)
    return output_path


def get_most_recent_file_in_dir(path: str, ext: Optional[str] = None) -> Optional[str]:
    """
    Gets the most recently created file in the specified path
    :param path: File path or glob pattern to check
    :param ext: File extension
    :return: Path to newest file in specified path with specified extension (None if no files in path)
    """
    if os.path.isdir(path):
        path = f"{path}/*"
    list_of_files = glob.glob(path)  # * means all if need specific format then *.csv
    if ext:
        if not ext.startswith("."):
            ext = f".{ext}"
        list_of_files = [file for file in list_of_files if os.path.splitext(file)[1] == ext]
    if list_of_files:
        latest_file = max(list_of_files, key=os.path.getctime)
        return latest_file
    else:
        return None


def get_file_as_wav(audio_file: str, desired_sample_rate: int, desired_sample_width: int = 2) -> wave.Wave_read:
    """
    Gets a wav file for the passed audio file.
    Args:
        audio_file: Path to audio file in arbitrary format
        desired_sample_rate: sample rate at which returned wav data should be encoded
        desired_sample_width: sample width at which returned wav data should be encoded
    Returns:
        Wave_read object encoded at the desired_sample_rate
    """

    audio_file = os.path.expanduser(audio_file)
    if not os.path.isfile(audio_file):
        raise FileNotFoundError
    try:
        file = wave.open(audio_file, 'rb')
        sample_rate = file.getframerate()
        sample_width = file.getsampwidth()
        if sample_rate == desired_sample_rate and sample_width == desired_sample_width:
            return file
    except wave.Error:
        pass
    except Exception as e:
        raise e
    audio = AudioSegment.from_file(audio_file)
    audio = audio.set_frame_rate(desired_sample_rate).set_sample_width(desired_sample_width)
    _, tempfile = mkstemp()
    audio.export(tempfile, format='wav').close()
    return wave.open(tempfile, 'rb')


def get_audio_file_stream(wav_file: str, sample_rate: int = 16000):
    """
    Creates a FileStream object for the specified wav_file with the specified output sample_rate.
    Args:
        wav_file: Path to file to read
        sample_rate: Desired output sample rate (None for wav_file sample rate)

    Returns:
        FileStream object for the passed audio file
    """
    class FileStream:
        MIN_S_TO_DEBUG = 5.0

        # How long between printing debug info to screen
        UPDATE_INTERVAL_S = 1.0

        def __init__(self, file_name):
            self.file = get_file_as_wav(file_name, sample_rate)
            self.sample_rate = self.file.getframerate()
            # if sample_rate and self.sample_rate != sample_rate:
            #     sound = AudioSegment.from_file(file_name, format='wav', frame_rate=self.sample_rate)
            #     sound = sound.set_frame_rate(sample_rate)
            #     _, tempfile = mkstemp()
            #     sound.export(tempfile, format='wav')
            #     self.file = wave.open(tempfile, 'rb')
            #     self.sample_rate = self.file.getframerate()
            self.size = self.file.getnframes()
            self.sample_width = self.file.getsampwidth()
            self.last_update_time = 0.0

            self.total_s = self.size / self.sample_rate / self.sample_width

        def calc_progress(self):
            return float(self.file.tell()) / self.size

        def read(self, chunk_size):

            progress = self.calc_progress()
            if progress == 1.0:
                raise EOFError

            return self.file.readframes(chunk_size)

        def close(self):
            self.file.close()

    if not os.path.isfile(wav_file):
        raise FileNotFoundError
    try:
        return FileStream(wav_file)
    except Exception as e:
        raise e


def audio_bytes_from_file(file_path: str) -> dict:
    """
        :param file_path: Path to file to read

        :returns {sample_rate, data, audio_format} if audio format is supported, empty dict otherwise
    """
    try:
        import librosa
    except ImportError:
        raise ImportError("librosa not available,"
                          " pip install neon-utils[audio]")
    except OSError as e:
        if repr(e) == "sndfile library not found":
            raise OSError("libsndfile missing, install via: "
                          "sudo apt install libsndfile1")
        else:
            raise e

    supported_audio_formats = ['mp3', 'wav']
    audio_format = file_path.split('.')[-1]
    if audio_format in supported_audio_formats:
        data, sample_rate = librosa.load(file_path)
        raw_audio_data = dict(sample_rate=sample_rate,
                              data=data,
                              audio_format=audio_format)
    else:
        LOG.warning(f'Failed to resolve audio format: {audio_format}')
        raw_audio_data = dict()

    return raw_audio_data


def audio_bytes_to_file(file_path: str, audio_data: List[float], sample_rate: int) -> str:
    """
        :param file_path: Path to file to write
        :param audio_data: array of audio data as float time series
        :param sample_rate: audio data sample rate

        :returns Path to saved file if saved successfully None otherwise
    """
    try:
        import soundfile as sf
    except ImportError:
        raise ImportError("soundfile not available,"
                          " pip install neon-utils[audio]")
    try:
        sf.write(file=file_path, data=audio_data, samplerate=sample_rate)
    except Exception as ex:
        LOG.error(f'Exception occurred while writing '
                  f'{audio_data} to {file_path}: {ex}')
        file_path = None
    return file_path


def resolve_neon_resource_file(res_name: str) -> Optional[str]:
    """
    Locates a resource file bundled with neon_utils or neon_core
    :param res_name: resource name (i.e. snd/start_listening.wav) to locate
    :return: path to resource or None if resource is not found
    """
    base_dir = os.path.join(os.path.dirname(__file__), "res")
    res_file = os.path.join(base_dir, res_name)
    if os.path.isfile(res_file):
        return res_file

    from neon_utils.packaging_utils import get_neon_core_root
    try:
        base_dir = os.path.join(get_neon_core_root(), "res")
    except FileNotFoundError:
        LOG.warning("No neon_core directory found")
        return None

    res_file = os.path.join(base_dir, res_name)
    if os.path.isfile(res_file):
        return res_file
    LOG.warning(f"Requested res_file not found: {res_file}")
    return None


def parse_skill_readme_file(readme_path: str) -> dict:
    """
    Parse a Neon skill README.md into a dictionary
    :param readme_path: absolute path to README.md file
    :return: dict of parsed data
    """
    from neon_utils.parse_utils import clean_quotes

    # Check passed path
    if not readme_path:
        raise ValueError("Null path")
    readme_path = os.path.expanduser(readme_path)
    if not os.path.isfile(readme_path):
        raise FileNotFoundError(f"{readme_path} is not a valid file")

    # Initialize parser params
    list_sections = ("examples", "incompatible skills", "platforms",
                     "categories", "tags", "credits")
    section = "header"
    category = None
    parsed_data = {}
    with open(readme_path, "r") as readme:
        lines = readme.readlines()

    def _check_section_start(ln: str):
        # Handle section start
        if ln.startswith("# ![](https://0000.us/klatchat/app/files/"
                         "neon_images/icons/neon_paw.png)"):
            # Old style title line
            parsed_data["title"] = ln.split(')', 1)[1].strip()
            parsed_data["icon"] = ln.split('(', 1)[1].split(')', 1)[0].strip()
            return
        elif section == "header" and ln.startswith("# <img src="):
            # Title line
            parsed_data["title"] = ln.split(">", 1)[1].strip()
            parsed_data["icon"] = ln.split("src=", 1)[1].split()[0]\
                .strip('"').strip("'").lstrip("./")
            return "summary"
        elif ln.startswith("# ") or ln.startswith("## "):
            # Top-level section
            if ln.startswith("## About"):
                # Handle Mycroft 'About' section
                return "description"
            elif ln.startswith("## Category"):
                # Handle 'Category' as 'Categories'
                return "categories"
            else:
                return line.lstrip("#").strip().lower()
        return

    def _format_readme_line(ln: str):
        nonlocal category
        if section == "incompatible skills":
            if not any((ln.startswith('-'), ln.startswith('*'))):
                return None
            parsed = clean_quotes(ln.lstrip('-').lstrip('*').lower().strip())
            if parsed.startswith('['):
                return parsed.split('(', 1)[1].split(')', 1)[0]
            return parsed
        if section == "examples":
            if not any((ln.startswith('-'), ln.startswith('*'))):
                return None
            parsed = clean_quotes(ln.lstrip('-').lstrip('*').strip())
            if parsed.split(maxsplit=1)[0].lower() == "neon":
                return parsed.split(maxsplit=1)[1]
            else:
                return parsed
        if section == "categories":
            parsed = ln.rstrip('\n').strip('*')
            if ln.startswith('**'):
                category = parsed
            return parsed
        if section == "credits":
            if ln.strip().startswith('['):
                return ln.split('[', 1)[1].split(']', 1)[0]
            return ln.rstrip('\n').lstrip('@')
        if section == "tags":
            return ln.lstrip('#').rstrip('\n')
        if section in list_sections:
            return clean_quotes(ln.lstrip('-').lstrip('*').lower().strip())
        return ln.rstrip('\n').rstrip()

    for line in lines:
        new_section = _check_section_start(line)
        if new_section:
            section = new_section
        elif line.strip():
            parsed_line = _format_readme_line(line)
            if not parsed_line:
                # Nothing to parse in this line
                continue
            if section in list_sections:
                if section not in parsed_data:
                    parsed_data[section] = list()
                parsed_data[section].append(parsed_line)
            else:
                if section not in parsed_data:
                    parsed_data[section] = parsed_line
                else:
                    parsed_data[section] = " ".join((parsed_data[section],
                                                     parsed_line))
    parsed_data["category"] = category or parsed_data.get("categories",
                                                          [""])[0]
    if parsed_data.get("incompatible skills"):
        parsed_data["incompatible_skills"] = \
            parsed_data.pop("incompatible skills")
    if parsed_data.get("credits") and len(parsed_data["credits"]) == 1:
        parsed_data["credits"] = parsed_data["credits"][0].split(' ')

    return parsed_data


def check_path_permissions(path: str) -> tuple:
    """
    Check current access permissions for the specified path
    :param path: file or directory path to check
    :return: tuple (read, write, execute)
    """
    path = os.path.expanduser(path)
    if not os.access(path, os.F_OK):
        raise FileNotFoundError(f"{path} does not exist")
    stat = (os.access(path, os.R_OK), os.access(path, os.W_OK),
            os.access(path, os.X_OK))
    return stat


def path_is_read_writable(path: str) -> bool:
    """
    Check if the specified path is readable and writable by the current user.
    :param path: str file path to check
    :return: True if path exists and is read/writable
    """
    if not path:
        return False
    try:
        path = os.path.expanduser(path)
        while path and not os.path.exists(path):
            path = os.path.dirname(path)
        stat = check_path_permissions(path)
        return all(stat[:2])
    except FileNotFoundError:
        return False


def create_file(filename: str):
    """
    Create the file filename and create any directories needed
    :param filename: Path to the file to be created
    """
    filename = os.path.expanduser(filename)
    if not path_is_read_writable(os.path.dirname(filename)):
        raise PermissionError(f"Insufficient permissions to create {filename}")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    # with NamedLock(filename): # TODO: Implement combo_lock with file lock support or add lock utils to neon_utils DM
    with open(filename, 'w') as f:
        f.write('')


def load_commented_file(filename: str, comment_prefix: str = '#') -> str:
    """
    Load a text file removing commented lines and trailing newlines
    :param filename: Path to the file to be created
    :param comment_prefix: Prefix characters to count as comments
    """
    # Check passed path
    if not filename:
        raise ValueError("Null path")
    filename = os.path.expanduser(filename)
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"{filename} is not a valid file")

    with open(filename) as f:
        lines = f.readlines()

    valid_lines = [line for line in lines if not
                   line.strip().startswith(comment_prefix)]

    return "".join(valid_lines).rstrip('\n')
