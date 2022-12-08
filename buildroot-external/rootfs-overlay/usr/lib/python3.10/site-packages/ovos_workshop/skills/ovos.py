import time
from copy import copy
from ovos_utils import camel_case_split, get_handler_name
# ensure mycroft can be imported
from ovos_utils import ensure_mycroft_import
from ovos_utils.log import LOG
from ovos_utils.messagebus import Message, dig_for_message, get_message_lang
from ovos_utils.skills.settings import PrivateSettings

ensure_mycroft_import()

from ovos_utils.skills import get_non_properties
from ovos_utils.intents import IntentBuilder, Intent, AdaptIntent
from ovos_utils.sound import play_audio
from ovos_workshop.patches.base_skill import MycroftSkill, FallbackSkill
from ovos_workshop.decorators.killable import killable_event, \
    AbortEvent, AbortQuestion
from ovos_workshop.skills.layers import IntentLayers
from ovos_workshop.resource_files import SkillResources
from ovos_utils.dialog import get_dialog
from ovos_utils.messagebus import create_wrapper


class OVOSSkill(MycroftSkill):
    """
    New features:
        - all patches for MycroftSkill class
        - self.private_settings
        - killable intents
        - IntentLayers
    """

    def __init__(self, *args, **kwargs):
        # loaded lang file resources
        self._lang_resources = {}
        super(OVOSSkill, self).__init__(*args, **kwargs)
        self.private_settings = None
        self._threads = []
        self._original_converse = self.converse
        self.intent_layers = IntentLayers()

    def bind(self, bus):
        super().bind(bus)
        if bus:
            # here to ensure self.skill_id is populated
            self.private_settings = PrivateSettings(self.skill_id)
            self.intent_layers.bind(self)

    def play_audio(self, filename):
        try:
            from mycroft.version import OVOS_VERSION_BUILD, OVOS_VERSION_MINOR, OVOS_VERSION_MAJOR
            if OVOS_VERSION_MAJOR >= 1 or \
                    OVOS_VERSION_MINOR > 0 or \
                    OVOS_VERSION_BUILD >= 4:
                self.bus.emit(Message("mycroft.audio.queue",
                                      {"filename": filename}))
        except:
            pass
        LOG.warning("self.play_audio requires ovos-core >= 0.0.4a45, falling back to local skill playback")
        play_audio(filename).wait()

    # lang support
    @property
    def lang(self):
        """Get the current active language."""
        lang = self.core_lang
        message = dig_for_message()
        if message:
            lang = get_message_lang(message)
        return lang.lower()

    # new public api, these are private methods in ovos-core
    # preference is given to ovos-core code to account for updates
    # but most functionality is otherwise duplicated here
    # simply with an underscore removed from the name
    @property
    def core_lang(self):
        """Get the configured default language."""
        if hasattr(self, "_core_lang"):
            return self._core_lang
        # reimplemented from ovos-core, means we are running in mycroft-core or older ovos version
        return self.config_core.get("lang", "en-us").lower()

    @property
    def secondary_langs(self):
        """Get the configured secondary languages, mycroft is not
        considered to be in these languages but i will load it's resource
        files. This provides initial support for multilingual input"""
        if hasattr(self, "_secondary_langs"):
            return self._secondary_langs
        # reimplemented from ovos-core, means we are running in mycroft-core or older ovos version
        return [l.lower() for l in self.config_core.get('secondary_langs', [])
                if l != self.core_lang]

    @property
    def native_langs(self):
        """Languages natively supported by core
        ie, resource files available and explicitly supported
        """
        if hasattr(self, "_native_langs"):
            return self._native_langs
        # reimplemented from ovos-core, means we are running in mycroft-core or older ovos version
        return [self.core_lang] + self.secondary_langs

    @property
    def alphanumeric_skill_id(self):
        """skill id converted to only alphanumeric characters
         Non alpha-numeric characters are converted to "_"

        Returns:
            (str) String of letters
        """
        if hasattr(self, "_alphanumeric_skill_id"):
            return self._alphanumeric_skill_id
        # reimplemented from ovos-core, means we are running in mycroft-core or older ovos version
        return ''.join(c if c.isalnum() else '_'
                       for c in str(self.skill_id))

    @property
    def resources(self):
        """Instantiates a ResourceFileLocator instance when needed.
        a new instance is always created to ensure self.lang
        reflects the active language and not the default core language
        """
        if hasattr(self, "_resources"):
            return self._resources
        # reimplemented from ovos-core, means we are running in mycroft-core or older ovos version
        return self.load_lang(self.root_dir, self.lang)

    def load_lang(self, root_directory=None, lang=None):
        """Instantiates a ResourceFileLocator instance when needed.
        a new instance is always created to ensure lang
        reflects the active language and not the default core language
        """
        if hasattr(self, "_load_lang"):
            return self._load_lang(root_directory, lang)
        # reimplemented from ovos-core, means we are running in mycroft-core or older ovos version
        lang = lang or self.lang
        root_directory = root_directory or self.root_dir
        if lang not in self._lang_resources:
            self._lang_resources[lang] = SkillResources(root_directory, lang, skill_id=self.skill_id)
        return self._lang_resources[lang]

    #
    def voc_match(self, *args, **kwargs):
        try:
            return super().voc_match(*args, **kwargs)
        except FileNotFoundError:
            return False

    def _register_decorated(self):
        """Register all intent handlers that are decorated with an intent.

        Looks for all functions that have been marked by a decorator
        and read the intent data from them.  The intent handlers aren't the
        only decorators used.  Skip properties as calling getattr on them
        executes the code which may have unintended side-effects
        """
        super()._register_decorated()
        for attr_name in get_non_properties(self):
            method = getattr(self, attr_name)
            if hasattr(method, 'intent_layers'):
                for layer_name, intent_files in \
                        getattr(method, 'intent_layers').items():
                    self.register_intent_layer(layer_name, intent_files)

            # TODO support for multiple converse handlers (?)
            if hasattr(method, 'converse'):
                self.converse = method

    def register_intent_layer(self, layer_name, intent_list):
        for intent_file in intent_list:
            if IntentBuilder is not None and isinstance(intent_file, IntentBuilder):
                intent = intent_file.build()
                name = intent.name
            elif Intent is not None and isinstance(intent_file, Intent):
                name = intent_file.name
            else:
                name = intent_file
            self.intent_layers.update_layer(layer_name, [name])

    # killable_events support
    def send_stop_signal(self, stop_event=None):
        msg = dig_for_message() or Message("mycroft.stop")
        # stop event execution
        if stop_event:
            self.bus.emit(msg.forward(stop_event))

        # stop TTS
        self.bus.emit(msg.forward("mycroft.audio.speech.stop"))

        # Tell ovos-core to stop recording (not in mycroft-core)
        self.bus.emit(msg.forward('recognizer_loop:record_stop'))

        # special non-ovos handling
        try:
            from mycroft.version import OVOS_VERSION_STR
        except ImportError:
            # NOTE: mycroft does not have an event to stop recording
            # this attempts to force a stop by sending silence to end STT step
            self.bus.emit(Message('mycroft.mic.mute'))
            time.sleep(1.5)  # the silence from muting should make STT stop recording
            self.bus.emit(Message('mycroft.mic.unmute'))

        time.sleep(0.5)  # if TTS had not yet started
        self.bus.emit(msg.forward("mycroft.audio.speech.stop"))

    # these methods are copied from ovos-core for compat with mycroft-core
    def _on_event_start(self, message, handler_info, skill_data):
        """Indicate that the skill handler is starting."""
        if handler_info:
            # Indicate that the skill handler is starting if requested
            msg_type = handler_info + '.start'
            message.context["skill_id"] = self.skill_id
            self.bus.emit(message.forward(msg_type, skill_data))

    def _on_event_end(self, message, handler_info, skill_data):
        """Store settings and indicate that the skill handler has completed
        """
        if self.settings != self._initial_settings:
            try:  # ovos-core
                self.settings.store()
                self._initial_settings = copy(self.settings)
            except:  # mycroft-core
                from mycroft.skills.settings import save_settings
                save_settings(self.settings_write_path, self.settings)
                self._initial_settings = dict(self.settings)
        if handler_info:
            msg_type = handler_info + '.complete'
            message.context["skill_id"] = self.skill_id
            self.bus.emit(message.forward(msg_type, skill_data))

    def _on_event_error(self, error, message, handler_info, skill_data, speak_errors):
        """Speak and log the error."""
        # Convert "MyFancySkill" to "My Fancy Skill" for speaking
        handler_name = camel_case_split(self.name)
        msg_data = {'skill': handler_name}
        speech = get_dialog('skill.error', self.lang, msg_data)
        if speak_errors:
            self.speak(speech)
        LOG.exception(error)
        # append exception information in message
        skill_data['exception'] = repr(error)
        if handler_info:
            # Indicate that the skill handler errored
            msg_type = handler_info + '.error'
            message = message or Message("")
            message.context["skill_id"] = self.skill_id
            self.bus.emit(message.forward(msg_type, skill_data))

    def add_event(self, name, handler, handler_info=None, once=False, speak_errors=True):
        """Create event handler for executing intent or other event.

        Args:
            name (string): IntentParser name
            handler (func): Method to call
            handler_info (string): Base message when reporting skill event
                                   handler status on messagebus.
            once (bool, optional): Event handler will be removed after it has
                                   been run once.
            speak_errors (bool, optional): Determines if an error dialog should be
                                           spoken to inform the user whenever
                                           an exception happens inside the handler
        """
        skill_data = {'name': get_handler_name(handler)}

        def on_error(error, message):
            if isinstance(error, AbortEvent):
                LOG.info("Skill execution aborted")
                self._on_event_end(message, handler_info, skill_data)
                return
            self._on_event_error(error, message, handler_info, skill_data, speak_errors)

        def on_start(message):
            self._on_event_start(message, handler_info, skill_data)

        def on_end(message):
            self._on_event_end(message, handler_info, skill_data)

        wrapper = create_wrapper(handler, self.skill_id, on_start, on_end,
                                 on_error)
        return self.events.add(name, wrapper, once)

    def __handle_stop(self, message):
        self.bus.emit(message.forward(self.skill_id + ".stop",
                                      context={"skill_id": self.skill_id}))
        super().__handle_stop(message)

    # abort get_response gracefully
    def _wait_response(self, is_cancel, validator, on_fail, num_retries):
        """Loop until a valid response is received from the user or the retry
        limit is reached.

        Arguments:
            is_cancel (callable): function checking cancel criteria
            validator (callbale): function checking for a valid response
            on_fail (callable): function handling retries

        """
        self._response = False
        self._real_wait_response(is_cancel, validator, on_fail, num_retries)
        while self._response is False:
            time.sleep(0.1)
        return self._response

    def __get_response(self):
        """Helper to get a reponse from the user

        Returns:
            str: user's response or None on a timeout
        """

        def converse(utterances, lang=None):
            converse.response = utterances[0] if utterances else None
            converse.finished = True
            return True

        # install a temporary conversation handler
        self.make_active()
        converse.finished = False
        converse.response = None
        self.converse = converse

        # 10 for listener, 5 for SST, then timeout
        # NOTE a threading event is not used otherwise we can't raise the
        # AbortEvent exception to kill the thread
        start = time.time()
        while time.time() - start <= 15 and not converse.finished:
            time.sleep(0.1)
            if self._response is not False:
                if self._response is None:
                    # aborted externally (if None)
                    self.log.debug("get_response aborted")
                converse.finished = True
                converse.response = self._response  # external override
        self.converse = self._original_converse
        return converse.response

    def _handle_killed_wait_response(self):
        self._response = None
        self.converse = self._original_converse

    @killable_event("mycroft.skills.abort_question", exc=AbortQuestion,
                    callback=_handle_killed_wait_response, react_to_stop=True)
    def _real_wait_response(self, is_cancel, validator, on_fail, num_retries):
        """Loop until a valid response is received from the user or the retry
        limit is reached.

        Arguments:
            is_cancel (callable): function checking cancel criteria
            validator (callbale): function checking for a valid response
            on_fail (callable): function handling retries

        """
        num_fails = 0
        while True:
            if self._response is not False:
                # usually None when aborted externally
                # also allows overriding returned result from other events
                return self._response

            response = self.__get_response()

            if response is None:
                # if nothing said, prompt one more time
                num_none_fails = 1 if num_retries < 0 else num_retries
                if num_fails >= num_none_fails:
                    self._response = None
                    return
            else:
                if validator(response):
                    self._response = response
                    return

                # catch user saying 'cancel'
                if is_cancel(response):
                    self._response = None
                    return

            num_fails += 1
            if 0 < num_retries < num_fails or self._response is not False:
                self._response = None
                return

            line = on_fail(response)
            if line:
                self.speak(line, expect_response=True)
            else:
                self.bus.emit(Message('mycroft.mic.listen',
                                      context={"skill_id": self.skill_id}))


class OVOSFallbackSkill(FallbackSkill, OVOSSkill):
    """ monkey patched mycroft fallback skill """

    def _register_decorated(self):
        """Register all intent handlers that are decorated with an intent.

        Looks for all functions that have been marked by a decorator
        and read the intent data from them.  The intent handlers aren't the
        only decorators used.  Skip properties as calling getattr on them
        executes the code which may have unintended side-effects
        """
        super()._register_decorated()
        for attr_name in get_non_properties(self):
            method = getattr(self, attr_name)
            if hasattr(method, 'fallback_priority'):
                self.register_fallback(method, method.fallback_priority)
