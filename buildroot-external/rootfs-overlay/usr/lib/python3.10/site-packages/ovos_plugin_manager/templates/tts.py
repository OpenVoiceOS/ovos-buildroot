"""
this module is meant to enable usage of mycroft plugins inside and outside
mycroft, importing from here will make things work as planned in mycroft,
but if outside mycroft things will still work

The main use case is for plugins to be used across different projects

## Differences from upstream

TTS:
- added automatic guessing of phonemes/visime calculation, enabling mouth
movements for all TTS engines (only mimic implements this in upstream)
- playback start call has been omitted and moved to init method
- init is called by mycroft, but non mycroft usage wont call it
- outside mycroft the enclosure is not set, bus is dummy and playback thread is not used
    - playback queue is not wanted when some module is calling get_tts
    - if playback was started on init then python scripts would never stop
        from mycroft.tts import TTSFactory
        engine = TTSFactory.create()
        engine.get_tts("hello world", "hello_world." + engine.audio_ext)
        # would hang here
        engine.playback.stop()
"""
import inspect
import random
import re
import subprocess
import threading
from os.path import isfile, join, splitext
from pathlib import Path
from queue import Queue, Empty
from threading import Thread
from time import time, sleep

import requests
from mycroft_bus_client.message import Message, dig_for_message
from ovos_utils import resolve_resource_file
from ovos_config import Configuration
from ovos_utils.enclosure.api import EnclosureAPI
from ovos_utils.file_utils import get_cache_directory
from ovos_utils.lang.visimes import VISIMES
from ovos_utils.log import LOG
from ovos_utils.messagebus import FakeBus as BUS
from ovos_utils.metrics import Stopwatch
from ovos_utils.signal import check_for_signal, create_signal
from ovos_utils.sound import play_audio

from ovos_plugin_manager.g2p import OVOSG2PFactory, find_g2p_plugins
from ovos_plugin_manager.templates.g2p import OutOfVocabulary
from ovos_plugin_manager.utils.tts_cache import TextToSpeechCache, hash_sentence
from ovos_plugin_manager.utils.config import get_plugin_config

EMPTY_PLAYBACK_QUEUE_TUPLE = (None, None, None, None, None)
SSML_TAGS = re.compile(r'<[^>]*>')


class PlaybackThread(Thread):
    """Thread class for playing back tts audio and sending
    viseme data to enclosure.
    """

    def __init__(self, queue):
        super(PlaybackThread, self).__init__()
        self.queue = queue
        self._terminated = False
        self._processing_queue = False
        self._paused = False
        self.enclosure = None
        self.p = None
        self._tts = []
        self.bus = None
        self._now_playing = None
        self.active_tts = None
        self._started = threading.Event()

    @property
    def is_running(self):
        return self._started.is_set() and not self._terminated

    def activate_tts(self, tts_id):
        self.active_tts = tts_id
        tts = self.get_attached_tts()
        if tts:
            tts.begin_audio()

    def deactivate_tts(self):
        if self.active_tts:
            tts = self.get_attached_tts()
            if tts:
                tts.end_audio()
        self.active_tts = None

    def init(self, tts):
        """DEPRECATED! Init the TTS Playback thread."""
        self.attach_tts(tts)
        self.set_bus(tts.bus)

    def set_bus(self, bus):
        """Provide bus instance to the TTS Playback thread.
        Args:
            bus (MycroftBusClient): bus client
        """
        self.bus = bus

    @property
    def tts(self):
        tts = self.get_attached_tts()
        if not tts and self._tts:
            return self._tts[0]
        return tts

    @tts.setter
    def tts(self, val):
        self.attach_tts(val)

    @property
    def attached_tts(self):
        return self._tts

    def attach_tts(self, tts):
        """Add TTS to be cache checked."""
        if tts not in self.attached_tts:
            self.attached_tts.append(tts)

    def detach_tts(self, tts):
        """Remove TTS from cache check."""
        if tts in self.attached_tts:
            self.attached_tts.remove(tts)

    def get_attached_tts(self, tts_id=None):
        tts_id = tts_id or self.active_tts
        if not tts_id:
            return
        for tts in self.attached_tts:
            if hasattr(tts, "tts_id"):
                # opm plugin
                if tts.tts_id == tts_id:
                    return tts

        for tts in self.attached_tts:
            if not hasattr(tts, "tts_id"):
                # non-opm plugin
                if tts.tts_name == tts_id:
                    return tts

    def clear_queue(self):
        """Remove all pending playbacks."""
        while not self.queue.empty():
            self.queue.get()
        try:
            self.p.terminate()
        except Exception:
            pass

    def begin_audio(self):
        """Perform beginning of speech actions."""
        # This check will clear the "signal", in case it is still there for some reasons
        check_for_signal("isSpeaking")
        # this will create it again
        create_signal("isSpeaking")
        # Create signals informing start of speech
        if self.bus:
            self.bus.emit(Message("recognizer_loop:audio_output_start"))
        else:
            LOG.warning("Speech started before bus was attached.")

    def end_audio(self, listen):
        """Perform end of speech output actions.
        Will inform the system that speech has ended and trigger the TTS's
        cache checks. Listening will be triggered if requested.
        Args:
            listen (bool): True if listening event should be emitted
        """
        if self.bus:
            # Send end of speech signals to the system
            self.bus.emit(Message("recognizer_loop:audio_output_end"))
            if listen:
                self.bus.emit(Message('mycroft.mic.listen'))
        else:
            LOG.warning("Speech started before bus was attached.")

        # This check will clear the filesystem IPC "signal"
        check_for_signal("isSpeaking")

    def on_start(self):
        self.blink(0.5)
        if not self._processing_queue:
            self._processing_queue = True
            self.begin_audio()

    def on_end(self, listen=False):
        if self._processing_queue:
            self.end_audio(listen)
            self._processing_queue = False

        # Clear cache for all attached tts objects
        # This is basically the only safe time
        for tts in self.attached_tts:
            tts.cache.curate()
        self.blink(0.2)

    def _play(self):
        listen = False
        tts_id = None
        try:
            if len(self._now_playing) == 6:
                # opm style with tts_id
                snd_type, data, visemes, ident, listen, tts_id = self._now_playing
            elif len(self._now_playing) == 5:
                # new mycroft style
                snd_type, data, visemes, ident, listen = self._now_playing
            else:
                # old mycroft style  TODO can this be deprecated? its very old
                snd_type, data, visemes, ident = self._now_playing

            self.activate_tts(tts_id)
            self.on_start()
            self.p = play_audio(data)
            if visemes:
                self.show_visemes(visemes)
            if self.p:
                self.p.communicate()
                self.p.wait()
            self.deactivate_tts()
            if self.queue.empty():
                self.on_end(listen)
        except Empty:
            pass
        except Exception as e:
            LOG.exception(e)
            if self._processing_queue:
                self.on_end(listen)
        self._now_playing = None

    def run(self, cb=None):
        """Thread main loop. Get audio and extra data from queue and play.

        The queue messages is a tuple containing
        snd_type: 'mp3' or 'wav' telling the loop what format the data is in
        data: path to temporary audio data
        videmes: list of visemes to display while playing
        listen: if listening should be triggered at the end of the sentence.

        Playback of audio is started and the visemes are sent over the bus
        the loop then wait for the playback process to finish before starting
        checking the next position in queue.

        If the queue is empty the tts.end_audio() is called possibly triggering
        listening.
        """
        self._paused = False
        self._started.set()
        while not self._terminated:
            while self._paused:
                sleep(0.2)
            try:
                self._now_playing = self.queue.get(timeout=2)
                self._play()
            except Exception as e:
                pass

    def show_visemes(self, pairs):
        """Send viseme data to enclosure

        Args:
            pairs (list): Visime and timing pair

        Returns:
            bool: True if button has been pressed.
        """
        if self.enclosure:
            self.enclosure.mouth_viseme(time(), pairs)

    def pause(self):
        """pause thread"""
        self._paused = True
        if self.p:
            self.p.terminate()

    def resume(self):
        """resume thread"""
        if self._now_playing:
            self._play()
        self._paused = False

    def clear(self):
        """Clear all pending actions for the TTS playback thread."""
        self.clear_queue()

    def blink(self, rate=1.0):
        """Blink mycroft's eyes"""
        if self.enclosure and random.random() < rate:
            self.enclosure.eyes_blink("b")

    def stop(self):
        """Stop thread"""
        self._now_playing = None
        self._terminated = True
        self.clear_queue()

    def shutdown(self):
        self.stop()
        for tts in self.attached_tts:
            self.detach_tts(tts)

    def __del__(self):
        self.shutdown()


class TTSContext:
    """ parses kwargs for valid signatures and extracts voice/lang optional parameters
    it will look for a requested voice in kwargs and inside the source Message data if available.
    voice can also be defined by a combination of language and gender,
    in that case the helper method get_voice will be used to resolve the final voice_id
    """

    def __init__(self, engine):
        self.engine = engine

    def get_message(self, kwargs):
        msg = kwargs.get("message") or dig_for_message()
        if msg and isinstance(msg, Message):
            return msg

    def get_lang(self, kwargs):
        # parse requested language for this TTS request
        # NOTE: this is ovos only functionality, not in mycroft-core!
        lang = kwargs.get("lang")
        message = self.get_message(kwargs)
        if not lang and message:
            # get lang from message object if possible
            lang = message.data.get("lang") or \
                   message.context.get("lang")
        return lang or self.engine.lang

    def get_gender(self, kwargs):
        gender = kwargs.get("gender")
        message = self.get_message(kwargs)
        if not gender and message:
            # get gender from message object if possible
            gender = message.data.get("gender") or \
                     message.context.get("gender")
        return gender

    def get_voice(self, kwargs):
        # parse requested voice for this TTS request
        # NOTE: this is ovos only functionality, not in mycroft-core!
        voice = kwargs.get("voice")
        message = self.get_message(kwargs)
        if not voice and message:
            # get voice from message object if possible
            voice = message.data.get("voice") or \
                    message.context.get("voice")

        if not voice:
            gender = self.get_gender(kwargs)
            if gender:
                lang = self.get_lang(kwargs)
                voice = self.engine.get_voice(gender, lang)

        return voice or self.engine.voice

    def get(self, kwargs=None):
        kwargs = kwargs or {}
        return self.get_lang(kwargs), self.get_voice(kwargs)

    def get_cache(self, kwargs=None):
        lang, voice = self.get(kwargs)
        return self.engine.get_cache(voice, lang)


class TTS:
    """TTS abstract class to be implemented by all TTS engines.

    It aggregates the minimum required parameters and exposes
    ``execute(sentence)`` and ``validate_ssml(sentence)`` functions.

    Arguments:
        lang (str):
        config (dict): Configuration for this specific tts engine
        validator (TTSValidator): Used to verify proper installation
        phonetic_spelling (bool): Whether to spell certain words phonetically
        ssml_tags (list): Supported ssml properties. Ex. ['speak', 'prosody']
    """
    queue = None
    playback = None

    def __init__(self, lang="en-us", config=None, validator=None,
                 audio_ext='wav', phonetic_spelling=True, ssml_tags=None):
        self.log_timestamps = False

        self.config = config or get_plugin_config(config, "tts")

        self.stopwatch = Stopwatch()
        self.tts_name = self.__class__.__name__
        self.bus = BUS()  # initialized in "init" step
        self.lang = lang or self.config.get("lang") or 'en-us'
        self.validator = validator or TTSValidator(self)
        self.phonetic_spelling = phonetic_spelling
        self.audio_ext = audio_ext
        self.ssml_tags = ssml_tags or []
        self.log_timestamps = self.config.get("log_timestamps", False)

        self.voice = self.config.get("voice") or "default"
        # TODO can self.filename be deprecated ? is it used anywhere at all?
        cache_dir = get_cache_directory(self.tts_name)
        self.filename = join(cache_dir, 'tts.' + self.audio_ext)

        random.seed()

        if TTS.queue is None:
            TTS.queue = Queue()

        self.context = TTSContext(self)

        # NOTE: self.playback.start() was moved to init method
        #   playback queue is not wanted if we only care about get_tts
        #   init is called by mycroft, but non mycroft usage wont call it,
        #   outside mycroft the enclosure is not set, bus is dummy and
        #   playback thread is not used
        self.spellings = self.load_spellings()

        self.caches = {
            self.tts_id: TextToSpeechCache(
                self.config, self.tts_id, self.audio_ext
            )}

        cfg = Configuration()
        g2pm = self.config.get("g2p_module")
        if g2pm:
            if g2pm in find_g2p_plugins():
                cfg.setdefault("g2p", {})
                globl = cfg["g2p"].get("module") or g2pm
                if globl != g2pm:
                    LOG.info(f"TTS requested {g2pm} explicitly, ignoring global module {globl} ")
                cfg["g2p"]["module"] = g2pm
            else:
                LOG.warning(f"TTS selected {g2pm}, but it is not available!")
        self.g2p = OVOSG2PFactory.create(cfg)
        self.cache.curate()

        self.add_metric({"metric_type": "tts.init"})

    @property
    def tts_id(self):
        lang, voice = self.context.get()
        return join(self.tts_name, voice, lang)

    @property
    def cache(self):
        return self.caches.get(self.tts_id) or \
               self.get_cache()

    @cache.setter
    def cache(self, val):
        self.caches[self.tts_id] = val

    def get_cache(self, voice=None, lang=None):
        lang = lang or self.lang
        voice = voice or self.voice or "default"
        tts_id = join(self.tts_name, voice, lang)
        if tts_id not in self.caches:
            self.caches[tts_id] = TextToSpeechCache(
                self.config, tts_id, self.audio_ext
            )
        return self.caches[tts_id]

    def handle_metric(self, metadata=None):
        """ receive timing metrics for diagnostics
        does nothing by default but plugins might use it, eg, NeonCore"""

    def add_metric(self, metadata=None):
        """ wraps handle_metric to catch exceptions and log timestamps """
        try:
            self.handle_metric(metadata)
            if self.log_timestamps:
                LOG.debug(f"time delta: {self.stopwatch.delta} metric: {metadata}")
        except Exception as e:
            LOG.exception(e)

    def load_spellings(self, config=None):
        """Load phonetic spellings of words as dictionary."""
        path = join('text', self.lang.lower(), 'phonetic_spellings.txt')
        try:
            spellings_file = resolve_resource_file(path, config=config)
        except:
            LOG.debug('Failed to locate phonetic spellings resouce file.')
            return {}
        if not spellings_file:
            return {}
        try:
            with open(spellings_file) as f:
                lines = filter(bool, f.read().split('\n'))
            lines = [i.split(':') for i in lines]
            return {key.strip(): value.strip() for key, value in lines}
        except ValueError:
            LOG.exception('Failed to load phonetic spellings.')
            return {}

    def begin_audio(self):
        """Helper function for child classes to call in execute()"""
        self.add_metric({"metric_type": "tts.start"})

    def end_audio(self, listen=False):
        """Helper cleanup function for child classes to call in execute().

        Arguments:
            listen (bool): DEPRECATED: indication if listening trigger should be sent.
        """
        self.add_metric({"metric_type": "tts.end"})
        self.stopwatch.stop()

    def init(self, bus=None):
        """ Performs intial setup of TTS object.

        Arguments:
            bus:    Mycroft messagebus connection
        """
        self.bus = bus or BUS()
        self._init_playback()
        self.add_metric({"metric_type": "tts.setup"})

    def _init_playback(self):
        # shutdown any previous thread
        if TTS.playback:
            TTS.playback.shutdown()

        TTS.playback = PlaybackThread(TTS.queue)
        TTS.playback.set_bus(self.bus)
        TTS.playback.attach_tts(self)
        if not TTS.playback.enclosure:
            TTS.playback.enclosure = EnclosureAPI(self.bus)
        TTS.playback.start()

    @property
    def enclosure(self):
        if not TTS.playback.enclosure:
            bus = TTS.playback.bus or self.bus
            TTS.playback.enclosure = EnclosureAPI(bus)
        return TTS.playback.enclosure

    @enclosure.setter
    def enclosure(self, val):
        TTS.playback.enclosure = val

    def get_tts(self, sentence, wav_file, lang=None):
        """Abstract method that a tts implementation needs to implement.

        Should get data from tts.

        Arguments:
            sentence(str): Sentence to synthesize
            wav_file(str): output file
            lang(str): requested language (optional), defaults to self.lang

        Returns:
            tuple: (wav_file, phoneme)
        """
        return "", None

    def modify_tag(self, tag):
        """Override to modify each supported ssml tag.

        Arguments:
            tag (str): SSML tag to check and possibly transform.
        """
        return tag

    @staticmethod
    def remove_ssml(text):
        """Removes SSML tags from a string.

        Arguments:
            text (str): input string

        Returns:
            str: input string stripped from tags.
        """
        return re.sub('<[^>]*>', '', text).replace('  ', ' ')

    @staticmethod
    def format_speak_tags(sentence: str, include_tags: bool = True) -> str:
        """
        Cleans up SSML tags for speech synthesis and ensures the phrase is
        wrapped in 'speak' tags and any excluded text is
        removed.
        Args:
            sentence: Input sentence to be spoken
            include_tags: Flag to include <speak> tags in returned string
        Returns:
            Cleaned sentence to pass to TTS
        """
        # Wrap sentence in speak tag if no tags present
        if "<speak>" not in sentence and "</speak>" not in sentence:
            to_speak = f"<speak>{sentence}</speak>"
        # Assume speak starts at the beginning of the sentence
        elif "<speak>" not in sentence:
            to_speak = f"<speak>{sentence}"
        # Assume speak ends at the end of the sentence
        elif "</speak>" not in sentence:
            to_speak = f"{sentence}</speak>"
        else:
            to_speak = sentence

        # Trim text outside of speak tags
        if not to_speak.startswith("<speak>"):
            to_speak = f"<speak>{to_speak.split('<speak>', 1)[1]}"

        if not to_speak.endswith("</speak>"):
            to_speak = f"{to_speak.split('</speak>', 1)[0]}</speak>"

        if to_speak == "<speak></speak>":
            return ""

        if include_tags:
            return to_speak
        else:
            return to_speak.lstrip("<speak>").rstrip("</speak>")

    def validate_ssml(self, utterance):
        """Check if engine supports ssml, if not remove all tags.

        Remove unsupported / invalid tags

        Arguments:
            utterance (str): Sentence to validate

        Returns:
            str: validated_sentence
        """

        # Validate speak tags
        if not self.ssml_tags or "speak" not in self.ssml_tags:
            self.format_speak_tags(utterance, False)
        elif self.ssml_tags and "speak" in self.ssml_tags:
            self.format_speak_tags(utterance)

        # if ssml is not supported by TTS engine remove all tags
        if not self.ssml_tags:
            return self.remove_ssml(utterance)

        # find ssml tags in string
        tags = SSML_TAGS.findall(utterance)

        for tag in tags:
            if any(supported in tag for supported in self.ssml_tags):
                utterance = utterance.replace(tag, self.modify_tag(tag))
            else:
                # remove unsupported tag
                utterance = utterance.replace(tag, "")

        # return text with supported ssml tags only
        return utterance.replace("  ", " ")

    def _preprocess_sentence(self, sentence):
        """Default preprocessing is no preprocessing.

        This method can be overridden to create chunks suitable to the
        TTS engine in question.

        Arguments:
            sentence (str): sentence to preprocess

        Returns:
            list: list of sentence parts
        """
        return [sentence]

    def execute(self, sentence, ident=None, listen=False, **kwargs):
        """Convert sentence to speech, preprocessing out unsupported ssml

        The method caches results if possible using the hash of the
        sentence.

        Arguments:
            sentence: (str) Sentence to be spoken
            ident: (str) Id reference to current interaction
            listen: (bool) True if listen should be triggered at the end
                    of the utterance.
        """
        sentence = self.validate_ssml(sentence)
        self.add_metric({"metric_type": "tts.ssml.validated"})
        create_signal("isSpeaking")
        self._execute(sentence, ident, listen, **kwargs)

    def _replace_phonetic_spellings(self, sentence):
        if self.phonetic_spelling:
            for word in re.findall(r"[\w']+", sentence):
                if word.lower() in self.spellings:
                    spelled = self.spellings[word.lower()]
                    sentence = sentence.replace(word, spelled)
        return sentence

    def _execute(self, sentence, ident, listen, **kwargs):
        self.stopwatch.start()
        sentence = self._replace_phonetic_spellings(sentence)
        chunks = self._preprocess_sentence(sentence)
        # Apply the listen flag to the last chunk, set the rest to False
        chunks = [(chunks[i], listen if i == len(chunks) - 1 else False)
                  for i in range(len(chunks))]
        self.add_metric({"metric_type": "tts.preprocessed",
                         "n_chunks": len(chunks)})

        lang, voice = self.context.get(kwargs)
        tts_id = join(self.tts_name, voice, lang)

        # synth -> queue for playback
        for sentence, l in chunks:
            # load from cache or synth + cache
            audio_file, phonemes = self.synth(sentence, **kwargs)

            # get visemes/mouth movements
            if phonemes:
                viseme = self.viseme(phonemes)
            else:
                viseme = []
                try:
                    viseme = self.g2p.utterance2visemes(sentence, lang)
                except OutOfVocabulary:
                    pass
                except:
                    # this one is unplanned, let devs know all the info so they can fix it
                    LOG.exception(f"Unexpected failure in G2P plugin: {self.g2p}")

            audio_ext = self._determine_ext(audio_file)

            if not viseme:
                # Debug level because this is expected in default installs
                LOG.debug(f"no mouth movements available! unknown visemes for {sentence}")

            TTS.queue.put(
                (audio_ext, str(audio_file), viseme, ident, l, tts_id)
            )
            self.add_metric({"metric_type": "tts.queued"})

    def _determine_ext(self, audio_file):
        # determine audio_ext on the fly
        # do not use the ext defined in the plugin since it might not match
        # some plugins support multiple extensions
        # or have caches in different extensions
        try:
            _, audio_ext = splitext(str(audio_file))
            return audio_ext[1:] or self.audio_ext
        except Exception as e:
            return self.audio_ext

    def synth(self, sentence, **kwargs):
        """ This method wraps get_tts
        several optional keyword arguments are supported
        sentence will be read/saved to cache"""
        self.add_metric({"metric_type": "tts.synth.start"})
        sentence_hash = hash_sentence(sentence)

        # parse requested language for this TTS request
        # NOTE: this is ovos/neon only functionality, not in mycroft-core!
        lang, voice = self.context.get(kwargs)
        kwargs["lang"] = lang
        kwargs["voice"] = voice

        cache = self.get_cache(voice, lang)  # cache per tts_id (lang/voice combo)

        # load from cache
        if sentence_hash in cache:
            audio, phonemes = self.get_from_cache(sentence, **kwargs)
            self.add_metric({"metric_type": "tts.synth.finished", "cache": True})
            return audio, phonemes

        # synth + cache
        audio = cache.define_audio_file(sentence_hash)

        # filter kwargs per plugin, different plugins expose different options
        #   mycroft-core -> no kwargs
        #   ovos -> lang + voice optional kwargs
        #   neon-core -> message
        kwargs = {k: v for k, v in kwargs.items()
                  if k in inspect.signature(self.get_tts).parameters
                  and k not in ["sentence", "wav_file"]}

        # finally do the TTS synth
        audio.path, phonemes = self.get_tts(sentence, str(audio), **kwargs)
        self.add_metric({"metric_type": "tts.synth.finished"})

        # cache sentence + phonemes
        self._cache_sentence(sentence, audio, phonemes, sentence_hash,
                             voice=voice, lang=lang)
        return audio, phonemes

    def _cache_phonemes(self, sentence, phonemes=None, sentence_hash=None):
        sentence_hash = sentence_hash or hash_sentence(sentence)
        if not phonemes:
            try:
                phonemes = self.g2p.utterance2arpa(sentence, self.lang)
                self.add_metric({"metric_type": "tts.phonemes.g2p"})
            except Exception as e:
                self.add_metric({"metric_type": "tts.phonemes.g2p.error", "error": str(e)})
        if phonemes:
            return self.save_phonemes(sentence_hash, phonemes)
        return None

    def _cache_sentence(self, sentence, audio_file, phonemes=None, sentence_hash=None,
                        voice=None, lang=None):
        sentence_hash = sentence_hash or hash_sentence(sentence)
        # RANT: why do you hate strings ChrisV?
        if isinstance(audio_file.path, str):
            audio_file.path = Path(audio_file.path)
        pho_file = self._cache_phonemes(sentence, phonemes, sentence_hash)
        cache = self.get_cache(voice=voice, lang=lang)
        cache.cached_sentences[sentence_hash] = (audio_file, pho_file)
        self.add_metric({"metric_type": "tts.synth.cached"})

    def get_from_cache(self, sentence, **kwargs):
        sentence_hash = hash_sentence(sentence)
        phonemes = None
        cache = self.context.get_cache(kwargs)
        audio_file, pho_file = cache.cached_sentences[sentence_hash]
        LOG.info(f"Found {audio_file.name} in TTS cache")
        if not pho_file:
            # guess phonemes from sentence + cache them
            pho_file = self._cache_phonemes(sentence, sentence_hash)
        if pho_file:
            phonemes = pho_file.load()
        return audio_file, phonemes

    def get_voice(self, gender, lang=None):
        """ map a language and gender to a valid voice for this TTS engine """
        lang = lang or self.lang
        return gender

    def viseme(self, phonemes):
        """Create visemes from phonemes.

        May be implemented to convert TTS phonemes into Mycroft mouth
        visuals.

        Arguments:
            phonemes (str): String with phoneme data

        Returns:
            list: visemes
        """
        visimes = []
        if phonemes:
            phones = str(phonemes).split(" ")
            for pair in phones:
                if ":" in pair:
                    pho_dur = pair.split(":")  # phoneme:duration
                    if len(pho_dur) == 2:
                        visimes.append((VISIMES.get(pho_dur[0], '4'),
                                        float(pho_dur[1])))
                else:
                    visimes.append((VISIMES.get(pair, '4'),
                                    float(0.2)))
        return visimes or None

    def clear_cache(self):
        """ Remove all cached files. """
        self.cache.clear()

    def save_phonemes(self, key, phonemes):
        """Cache phonemes

        Arguments:
            key (str):        Hash key for the sentence
            phonemes (str):   phoneme string to save
        """
        phoneme_file = self.cache.define_phoneme_file(key)
        phoneme_file.save(phonemes)
        return phoneme_file

    def load_phonemes(self, key):
        """Load phonemes from cache file.

        Arguments:
            key (str): Key identifying phoneme cache
        """
        phoneme_file = self.cache.define_phoneme_file(key)
        return phoneme_file.load()

    def stop(self):
        if TTS.playback:
            try:
                TTS.playback.stop()
            except Exception as e:
                pass
        self.add_metric({"metric_type": "tts.stop"})

    def shutdown(self):
        self.stop()
        if TTS.playback:
            TTS.playback.detach_tts(self)

    def __del__(self):
        self.shutdown()

    @property
    def available_languages(self) -> set:
        """Return languages supported by this TTS implementation in this state
        This property should be overridden by the derived class to advertise
        what languages that engine supports.
        Returns:
            set: supported languages
        """
        return set()


class TTSValidator:
    """TTS Validator abstract class to be implemented by all TTS engines.

    It exposes and implements ``validate(tts)`` function as a template to
    validate the TTS engines.
    """

    def __init__(self, tts):
        self.tts = tts

    def validate(self):
        self.validate_dependencies()
        self.validate_instance()
        self.validate_filename()
        self.validate_lang()
        self.validate_connection()

    def validate_dependencies(self):
        """Determine if all the TTS's external dependencies are satisfied."""
        pass

    def validate_instance(self):
        pass

    def validate_filename(self):
        pass

    def validate_lang(self):
        """Ensure the TTS supports current language."""

    def validate_connection(self):
        """Ensure the TTS can connect to it's backend.

        This can mean for example being able to launch the correct executable
        or contact a webserver.
        """

    def get_tts_class(self):
        """Return TTS class that this validator is for."""


class ConcatTTS(TTS):
    def __init__(self, *args, **kwargs):
        super(ConcatTTS, self).__init__(*args, **kwargs)
        self.time_step = float(self.config.get("time_step", 0.1))
        if self.time_step < 0.1:
            self.time_step = 0.1
        self.sound_files_path = self.config.get("sounds")
        self.channels = self.config.get("channels", "1")
        self.rate = self.config.get("rate", "16000")

    def sentence_to_files(self, sentence):
        """ list of ordered files to concatenate and form final wav file
        return files (list) , phonemes (list)
        """
        raise NotImplementedError

    def concat(self, files, wav_file):
        """ generate output wav file from input files """
        cmd = ["sox"]
        for file in files:
            if not isfile(file):
                continue
            cmd.append("-c")
            cmd.append(self.channels)
            cmd.append("-r")
            cmd.append(self.rate)
            cmd.append(file)

        cmd.append(wav_file)
        cmd.append("channels")
        cmd.append(self.channels)
        cmd.append("rate")
        cmd.append(self.rate)
        LOG.info(subprocess.check_output(cmd))
        return wav_file

    def get_tts(self, sentence, wav_file, lang=None):
        """
            get data from tts.

            Args:
                sentence(str): Sentence to synthesize
                wav_file(str): output file

            Returns:
                tuple: (wav_file, phoneme)
        """
        files, phonemes = self.sentence_to_files(sentence)
        wav_file = self.concat(files, wav_file)
        return wav_file, phonemes


class RemoteTTSException(Exception):
    pass


class RemoteTTSTimeoutException(RemoteTTSException):
    pass


class RemoteTTS(TTS):
    """
    Abstract class for a Remote TTS engine implementation.
    This class is only provided for backwards compatibility
    Usage is discouraged
    """

    def __init__(self, lang, config, url, api_path, validator):
        super(RemoteTTS, self).__init__(lang, config, validator)
        self.api_path = api_path
        self.auth = None
        self.url = config.get('url', url).rstrip('/')

    def build_request_params(self, sentence):
        pass

    def get_tts(self, sentence, wav_file, lang=None):
        r = requests.get(
            self.url + self.api_path, params=self.build_request_params(sentence),
            timeout=10, verify=False, auth=self.auth)
        if r.status_code != 200:
            return None
        with open(wav_file, 'wb') as f:
            f.write(r.content)
        return wav_file, None
