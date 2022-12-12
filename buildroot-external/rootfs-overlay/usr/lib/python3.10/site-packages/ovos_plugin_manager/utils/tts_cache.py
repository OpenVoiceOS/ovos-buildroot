import hashlib
import json
import os
from os.path import join
import shutil
from pathlib import Path
from stat import S_ISREG, ST_MTIME, ST_MODE, ST_SIZE

from ovos_config.locations import get_xdg_cache_save_path
from ovos_utils.file_utils import get_cache_directory as get_tmp_cache_dir
from ovos_utils.log import LOG


def hash_sentence(sentence: str):
    """Convert the sentence into a hash value used for the file name

    Args:
        sentence: The sentence to be cached
    """
    encoded_sentence = sentence.encode("utf-8", "ignore")
    sentence_hash = hashlib.md5(encoded_sentence).hexdigest()
    return sentence_hash


def hash_from_path(path: Path) -> str:
    """Returns hash from a given path.

    Simply removes extension and folder structure leaving the hash.

    NOTE: this does not do any hashing at all and naming is misleading
          however we keep the method around for backwards compat imports
          this is exclusively for usage with cached TTS files

    Args:
        path: path to get hash from

    Returns:
        Hash reference for file.
    """
    # NOTE: this does not do any hashing at all and naming is misleading
    # however we keep the method around for backwards compat imports
    # this is assumed to be used only to load cached TTS which is already named with an hash
    return path.with_suffix('').name


def mb_to_bytes(size):
    """Takes a size in MB and returns the number of bytes.

    Args:
        size(int/float): size in Mega Bytes

    Returns:
        (int/float) size in bytes
    """
    return size * 1024 * 1024


def _get_cache_entries(directory):
    """Get information tuple for all regular files in directory.

    Args:
        directory (str): path to directory to check

    Returns:
        (tuple) (modification time, size, filepath)
    """
    entries = (os.path.join(directory, fn) for fn in os.listdir(directory))
    entries = ((os.stat(path), path) for path in entries)

    # leave only regular files, insert modification date
    return ((stat[ST_MTIME], stat[ST_SIZE], path)
            for stat, path in entries if S_ISREG(stat[ST_MODE]))


def _delete_oldest(entries, bytes_needed):
    """Delete files with oldest modification date until space is freed.

    Args:
        entries (tuple): file + file stats tuple
        bytes_needed (int): disk space that needs to be freed

    Returns:
        (list) all removed paths
    """
    deleted_files = []
    space_freed = 0
    for moddate, fsize, path in sorted(entries):
        try:
            os.remove(path)
            space_freed += fsize
            deleted_files.append(path)
        except Exception:
            pass

        if space_freed > bytes_needed:
            break  # deleted enough!

    return deleted_files


def curate_cache(directory, min_free_percent=5.0, min_free_disk=50):
    """Clear out the directory if needed.

    The curation will only occur if both the precentage and actual disk space
    is below the limit. This assumes all the files in the directory can be
    deleted as freely.

    Args:
        directory (str): directory path that holds cached files
        min_free_percent (float): percentage (0.0-100.0) of drive to keep free,
                                  default is 5% if not specified.
        min_free_disk (float): minimum allowed disk space in MB, default
                               value is 50 MB if not specified.
    """
    # Simpleminded implementation -- keep a certain percentage of the
    # disk available.
    # TODO: Would be easy to add more options, like whitelisted files, etc.
    deleted_files = []

    # Get the disk usage statistics bout the given path
    space = shutil.disk_usage(directory)

    percent_free = space.free * 100 / space.total

    min_free_disk = mb_to_bytes(min_free_disk)

    if percent_free < min_free_percent and space.free < min_free_disk:
        LOG.info('Low diskspace detected, cleaning cache')
        # calculate how many bytes we need to delete
        bytes_needed = (min_free_percent - percent_free) / 100.0 * space.total
        bytes_needed = int(bytes_needed + 1.0)

        # get all entries in the directory w/ stats
        entries = _get_cache_entries(directory)
        # delete as many as needed starting with the oldest
        deleted_files = _delete_oldest(entries, bytes_needed)

    return deleted_files


class AudioFile:
    def __init__(self, cache_dir: Path, sentence_hash: str, file_type: str):
        self.name = f"{sentence_hash}.{file_type}"
        if isinstance(cache_dir, str):
            cache_dir = Path(cache_dir)
        self.path = cache_dir.joinpath(self.name)
        self.audio_data = None

    def save(self, audio: bytes):
        """Write a TTS cache file containing the audio to be spoken.
        Args:
            audio: TTS inference of a sentence
        """
        try:
            self.audio_data = audio
            with open(self.path, "wb") as audio_file:
                audio_file.write(audio)
        except Exception:
            LOG.exception(f"Failed to write {self.name} to cache")

    def load(self):
        """Load audio data from cached file."""
        if self.path.exists():
            try:
                with open(self.path, "rb") as audio:
                    self.audio_data = audio.read()
            except Exception:
                LOG.exception(f"Failed to read {self.name} audio data from cache")
        return self.audio_data

    def exists(self):
        return self.path.exists()

    def __str__(self):
        return str(self.path)


class PhonemeFile:
    def __init__(self, cache_dir: Path, sentence_hash: str):
        self.name = f"{sentence_hash}.pho"
        if isinstance(cache_dir, str):
            cache_dir = Path(cache_dir)
        self.path = cache_dir.joinpath(self.name)
        self.phonemes = None

    def load(self):
        """Load phonemes from cache file."""
        if self.path.exists():
            try:
                with open(self.path) as phoneme_file:
                    phonemes = phoneme_file.read().strip()
                self.phonemes = json.loads(phonemes)
            except Exception:
                LOG.exception(f"Failed to read {self.name} phonemes from cache")
        return self.phonemes

    def save(self, phonemes):
        """Write a TTS cache file containing the phoneme to be displayed.
        Args:
            phonemes: instructions for how to make the mouth on a device move
        """
        self.phonemes = phonemes
        try:
            rec = json.dumps(phonemes)
            with open(self.path, "w") as phoneme_file:
                phoneme_file.write(rec)
        except Exception:
            LOG.error(f"Failed to write {self.name} to cache")

    def exists(self):
        return self.path.exists()

    def __str__(self):
        return str(self.path)


class TextToSpeechCache:
    """Class for all persistent and temporary caching operations."""

    def __init__(self, tts_config, tts_name, audio_file_type):
        self.config = tts_config
        self.tts_name = tts_name
        self.audio_file_type = audio_file_type

        persistent_cache = self.config.get("preloaded_cache") or \
                           join(get_xdg_cache_save_path(), tts_name)
        tmp_cache = get_tmp_cache_dir(f"tts/{tts_name}")
        os.makedirs(tmp_cache, exist_ok=True)
        os.makedirs(persistent_cache, exist_ok=True)

        self.persistent_cache_dir = Path(persistent_cache)
        self.temporary_cache_dir = Path(tmp_cache)
        self.cached_sentences = {}
        # curate cache if disk usage is above min %
        self.min_free_percent = self.config.get("min_free_percent", 75)
        # save to permanent cache settings
        self.persist = self.config.get("persist_cache", False)
        # only persist if utterance is spoken >= N times
        self.persist_thresh = self.config.get("persist_thresh", 1)
        self._sentence_count = {}

    def __contains__(self, sha):
        """The cache contains a SHA if it knows of it and it exists on disk."""
        if sha not in self.cached_sentences:
            return False  # Doesn't know of it
        else:
            # Audio file must exist, phonemes are optional.
            audio, phonemes = self.cached_sentences[sha]
            return (audio.exists() and
                    (phonemes is None or phonemes.exists()))

    def load_persistent_cache(self):
        """There may be files pre-loaded in the persistent cache directory
        prior to run time, such as pre-recorded audio files.
        """
        if self.persistent_cache_dir is not None:
            self._load_existing_audio_files()
            self._load_existing_phoneme_files()
            LOG.info("Persistent TTS cache files loaded successfully.")

    def _load_existing_audio_files(self):
        """Find the TTS audio files already in the persistent cache."""
        glob_pattern = "*." + self.audio_file_type
        for file_path in self.persistent_cache_dir.glob(glob_pattern):
            sentence_hash = file_path.name.split(".")[0]
            audio_file = self.define_audio_file(sentence_hash, persistent=True)
            self.cached_sentences[sentence_hash] = audio_file, None

    def _load_existing_phoneme_files(self):
        """Find the TTS phoneme files already in the persistent cache.
        A phoneme file is no good without an audio file to pair it with.  If
        no audio file matches, do not load the phoneme.
        """
        for file_path in self.persistent_cache_dir.glob("*.pho"):
            sentence_hash = file_path.name.split(".")[0]
            cached_sentence = self.cached_sentences.get(sentence_hash)
            if cached_sentence is not None:
                audio_file = cached_sentence[0]
                phoneme_file = self.define_phoneme_file(sentence_hash, persistent=True)
                self.cached_sentences[sentence_hash] = audio_file, phoneme_file

    def clear(self):
        """Remove all files from the temporary cache."""
        for cache_file_path in self.temporary_cache_dir.iterdir():
            if cache_file_path.is_dir():
                for sub_path in cache_file_path.iterdir():
                    if sub_path.is_file():
                        sub_path.unlink()
            elif cache_file_path.is_file():
                cache_file_path.unlink()

    def curate(self):
        """Remove cache data if disk space is running low."""
        files_removed = curate_cache(str(self.temporary_cache_dir),
                                     min_free_percent=self.min_free_percent)
        hashes = set([hash_from_path(Path(path)) for path in files_removed])
        for sentence_hash in hashes:
            if sentence_hash in self.cached_sentences:
                self.cached_sentences.pop(sentence_hash)

    def define_audio_file(self, sentence_hash: str, persistent=False) -> AudioFile:
        """Build an instance of an object representing an audio file."""
        if persistent or self._should_persist(sentence_hash):
            audio_file = AudioFile(
                self.persistent_cache_dir, sentence_hash, self.audio_file_type
            )
        else:
            audio_file = AudioFile(
                self.temporary_cache_dir, sentence_hash, self.audio_file_type
            )
        return audio_file

    def define_phoneme_file(self, sentence_hash: str, persistent=False) -> PhonemeFile:
        """Build an instance of an object representing an phoneme file."""
        if persistent or self._should_persist(sentence_hash):
            phoneme_file = PhonemeFile(self.persistent_cache_dir, sentence_hash)
        else:
            phoneme_file = PhonemeFile(self.temporary_cache_dir, sentence_hash)
        return phoneme_file

    def _should_persist(self, sentence_hash: str):
        if self.persist:
            if sentence_hash not in self._sentence_count:
                self._sentence_count[sentence_hash] = 0
            self._sentence_count[sentence_hash] += 1
            if self._sentence_count[sentence_hash] >= self.persist_thresh:
                return True
        return False
