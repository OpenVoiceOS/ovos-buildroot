from itertools import chain
from os import listdir
from os.path import isdir, exists

from mycroft_bus_client.message import dig_for_message
from ovos_config.config import read_mycroft_config
from ovos_utils import get_handler_name
from ovos_utils.dialog import join_list, load_dialogs, get_dialog
from ovos_utils.enclosure.api import EnclosureAPI
from ovos_utils.events import *
from ovos_utils.events import EventContainer
from ovos_utils.events import create_wrapper
from ovos_utils.file_utils import *
from ovos_utils.file_utils import resolve_resource_file
from ovos_utils.gui import GUIInterface
from ovos_utils.intents.intent_service_interface import \
    IntentServiceInterface, munge_intent_parser
from ovos_utils.intents.intent_service_interface import munge_regex
from ovos_utils.log import LOG
from ovos_utils.messagebus import get_mycroft_bus
from ovos_utils.parse import match_one
from ovos_utils.skills.audioservice import AudioServiceInterface
from ovos_utils.skills.settings import PrivateSettings
from ovos_utils.sound import wait_while_speaking

from ovos_utils.skills import get_non_properties
from ovos_utils.intents import IntentBuilder, Intent, AdaptIntent
from ovos_workshop.decorators import *
from ovos_workshop.decorators.killable import killable_event, \
    AbortEvent, AbortQuestion
from ovos_workshop.decorators.layers import IntentLayers
from ovos_workshop.resource_files import SkillResources, find_resource

# LF imports are only used in ask_selection, they are optional and provide
# numeric input support, eg. "select the first option"
try:
    from lingua_franca.format import pronounce_number
    from lingua_franca.parse import extract_number
except:
    def pronounce_number(n, *args, **kwargs):
        return str(n)


    def extract_number(*args, **kwargs):
        return None


class OVOSAbstractApplication:
    def __init__(self, skill_id, bus=None, resources_dir=None, lang=None,
                 settings=None, gui=None):
        self.skill_id = skill_id
        self._lang_resources = {}
        self.res_dir = resources_dir  # TODO or some default xdg dir
        try:
            self.config_core = read_mycroft_config()
        except:
            self.config_core = {}
        self._core_lang = lang or self.config_core.get("lang", "en-us")

        self.voc_match_cache = {}
        self._threads = []
        self._original_converse = self.converse
        self._dedicated_bus = False

        self.bus = None
        self.enclosure = None
        self.audio_service = None
        if settings is None:
            settings = PrivateSettings(self.skill_id)
        self.settings = settings
        self.intent_service = IntentServiceInterface()
        self.events = EventContainer()
        self.intent_service.set_id(self.skill_id)
        self.gui = gui or GUIInterface(self.skill_id)
        self.intent_layers = IntentLayers()
        if bus:
            self.bind(bus)

    def bind(self, bus=None):
        if bus:
            self._dedicated_bus = False
        else:
            self._dedicated_bus = True
            bus = get_mycroft_bus()
        self.bus = bus
        self.gui.set_bus(self.bus)
        self.events.set_bus(self.bus)
        self.intent_service.set_bus(self.bus)
        self.intent_layers.bind(self)
        self.enclosure = EnclosureAPI(self.bus)
        self.audio_service = AudioServiceInterface(self.bus)
        self._register_bus_handlers()
        self._register_decorated()

    def _register_bus_handlers(self):
        self.add_event('mycroft.stop', self.__handle_stop)
        self.add_event('mycroft.skill.enable_intent',
                       self._handle_enable_intent)
        self.add_event('mycroft.skill.disable_intent',
                       self._handle_disable_intent)
        self.add_event('mycroft.skill.set_cross_context',
                       self._handle_set_cross_context)
        self.add_event('mycroft.skill.remove_cross_context',
                       self._handle_remove_cross_context)

    def stop(self):
        pass

    def __handle_stop(self, message):
        """Handler for the "mycroft.stop" signal. Runs the user defined
        `stop()` method.
        """
        try:
            # message to stop killable events
            self.bus.emit(Message(self.skill_id + ".stop",
                                  context={"skill_id": self.skill_id}))
            if self.stop():
                self.bus.emit(message.reply("mycroft.stop.handled",
                                            {"by": "skill:" + self.skill_id},
                                            {"skill_id": self.skill_id}))
        except Exception as e:
            LOG.exception(e)
            LOG.error(f'Failed to stop skill: {self.skill_id}')

    def default_shutdown(self):
        pass

    def shutdown(self):
        self.stop()
        self.default_shutdown()
        self.events.clear()
        self.bus.emit(
            Message('detach_skill',
                    {'skill_id': str(self.skill_id) + ':'},
                    {"skill_id": self.skill_id}))
        if self._dedicated_bus:
            self.bus.close()

    # localization
    @property
    def lang(self):
        """Get the current language."""
        message = dig_for_message()
        if message:
            return message.data.get("lang") or self._core_lang
        return self._core_lang

    @property
    def secondary_langs(self):
        """Get the configured secondary languages, mycroft is not
        considered to be in these languages but i will load it's resource
        files. This provides initial support for multilingual input
        """
        return [l for l in self.config_core.get('secondary_langs', [])
                if l != self._core_lang]

    @property
    def native_langs(self):
        """Languages natively supported by core
        ie, resource files available and explicitly supported
        """
        valid = set([l.lower() for l in self.secondary_langs
                     if '-' in l and l != self._core_lang] + [self._core_lang])
        return list(valid)

    @property
    def alphanumeric_skill_id(self):
        """skill id converted to only alphanumeric characters
         Non alpha-numeric characters are converted to "_"

        Returns:
            (str) String of letters
        """
        return ''.join(c if c.isalnum() else '_'
                       for c in str(self.skill_id))

    @property
    def resources(self):
        """Instantiates a ResourceFileLocator instance when needed.
        a new instance is always created to ensure self.lang
        reflects the active language and not the default core language
        """
        return self.load_lang(self.res_dir, self.lang)

    @property
    def location(self):
        """Get the JSON data holding location information."""
        # TODO: Allow to override this for devices that contain a GPS.
        return self.config_core.get('location')

    @property
    def location_timezone(self):
        """Get the timezone code, such as 'America/Los_Angeles'"""
        loc = self.location
        if type(loc) is dict and loc['timezone']:
            return loc['timezone']['code']
        return None

    def get_language_dir(self, base_path=None, lang=None):
        """ checks for all language variations and returns best path
        eg, if lang is set to pt-pt but only pt-br resources exist,
        those will be loaded instead of failing, or en-gb vs en-us and so on
        """
        base_path = base_path or self.res_dir
        lang = lang or self.lang
        lang_path = join(base_path, lang)

        # base_path/en-us
        if isdir(lang_path):
            return lang_path
        if "-" in lang:
            lang2 = lang.split("-")[0]
            # base_path/en
            general_lang_path = join(base_path, lang2)
            if isdir(general_lang_path):
                return general_lang_path
        else:
            lang2 = lang

        # base_path/en-uk, base_path/en-au...
        if isdir(base_path):
            # TODO how to choose best local dialect?
            for path in [join(base_path, f)
                         for f in listdir(base_path) if f.startswith(lang2)]:
                if isdir(path):
                    return path
        return join(base_path, lang)

    # messagebus
    def add_event(self, name, handler, handler_info=None, once=False):
        """Create event handler for executing intent or other event.

        Args:
            name (string): IntentParser name
            handler (func): Method to call
            handler_info (string): Base message when reporting skill event
                                   handler status on messagebus.
            once (bool, optional): Event handler will be removed after it has
                                   been run once.
        """
        skill_data = {'name': get_handler_name(handler)}

        def on_error(error, msg):
            """Speak and log the error."""
            if not isinstance(error, AbortEvent):
                LOG.exception(error)
                msg_data = {'skill': self.skill_id}
                utt = get_dialog('skill.error', self.lang, msg_data)
                self.speak(utt)
                # append exception information in message
                skill_data['exception'] = repr(error)
                if handler_info:
                    # Indicate that the skill handler errored
                    msg_type = handler_info + '.error'
                    msg = msg or Message("")
                    msg.context["skill_id"] = self.skill_id
                    self.bus.emit(msg.forward(msg_type, skill_data))
            else:
                LOG.info("Skill execution aborted")

        def on_start(message):
            """Indicate that the skill handler is starting."""
            if handler_info:
                # Indicate that the skill handler is starting if requested
                msg_type = handler_info + '.start'
                message.context["skill_id"] = self.skill_id
                self.bus.emit(message.forward(msg_type, skill_data))

        def on_end(message):
            """Store settings and indicate that the skill handler has completed
            """
            if handler_info:
                msg_type = handler_info + '.complete'
                message.context["skill_id"] = self.skill_id
                self.bus.emit(message.forward(msg_type, skill_data))

        wrapper = create_wrapper(handler, self.skill_id,
                                 on_start, on_end, on_error)
        return self.events.add(name, wrapper, once)

    def remove_event(self, name):
        """Removes an event from bus emitter and events list.

        Args:
            name (string): Name of Intent or Scheduler Event
        Returns:
            bool: True if found and removed, False if not found
        """
        return self.events.remove(name)

    # resource file loading
    def load_lang(self, root_directory=None, lang=None):
        """Instantiates a ResourceFileLocator instance when needed.
        a new instance is always created to ensure lang
        reflects the active language and not the default core language
        """
        lang = lang or self.lang
        root_directory = root_directory or self.res_dir
        if lang not in self._lang_resources:
            self._lang_resources[lang] = SkillResources(root_directory, lang, skill_id=self.skill_id)
        return self._lang_resources[lang]

    def load_data_files(self, root_directory=None):
        """Called by the skill loader to load intents, dialogs, etc.

        Args:
            root_directory (str): root folder to use when loading files.
        """
        root_directory = root_directory or self.res_dir
        self.load_dialog_files(root_directory)
        self.load_vocab_files(root_directory)
        self.load_regex_files(root_directory)

    def load_dialog_files(self, root_directory):
        root_directory = root_directory or self.res_dir
        for lang in self.native_langs:
            resources = self.load_lang(root_directory, lang)
            if resources.types.dialog.base_directory is None:
                LOG.debug(f'No dialog loaded for {lang}')

    def load_vocab_files(self, root_directory):
        """ Load vocab files found under root_directory.

        Args:
            root_directory (str): root folder to use when loading files
        """
        root_directory = root_directory or self.res_dir
        for lang in self.native_langs:
            resources = self.load_lang(root_directory, lang)
            if resources.types.vocabulary.base_directory is None:
                LOG.debug(f'No vocab loaded for {lang}')
            else:
                skill_vocabulary = resources.load_skill_vocabulary(
                    self.alphanumeric_skill_id
                )
                # For each found intent register the default along with any aliases
                for vocab_type in skill_vocabulary:
                    for line in skill_vocabulary[vocab_type]:
                        entity = line[0]
                        aliases = line[1:]
                        self.intent_service.register_adapt_keyword(
                            vocab_type, entity, aliases, lang)

    def load_regex_files(self, root_directory):
        """ Load regex files found under the skill directory.

        Args:
            root_directory (str): root folder to use when loading files
        """
        root_directory = root_directory or self.res_dir
        for lang in self.native_langs:
            resources = self.load_lang(root_directory, lang)
            if resources.types.regex.base_directory is not None:
                regexes = resources.load_skill_regex(self.alphanumeric_skill_id)
                for regex in regexes:
                    self.intent_service.register_adapt_regex(regex, lang)

    # resource file helpers
    def find_resource(self, res_name, res_dirname=None, lang=None):
        """Find a resource file.

        Searches for the given filename using this scheme:

        1. Search the resource lang directory:

           <skill>/<res_dirname>/<lang>/<res_name>

        2. Search the resource directory:

           <skill>/<res_dirname>/<res_name>

        3. Search the locale lang directory or other subdirectory:

           <skill>/locale/<lang>/<res_name> or

           <skill>/locale/<lang>/.../<res_name>

        Args:
            res_name (string): The resource name to be found
            res_dirname (string, optional): A skill resource directory, such
                                            'dialog', 'vocab', 'regex' or 'ui'.
                                            Defaults to None.
            lang (string, optional): language folder to be used.
                                     Defaults to self.lang.

        Returns:
            string: The full path to the resource file or None if not found
        """
        lang = lang or self.lang
        x = find_resource(res_name, self.res_dir, res_dirname, lang)
        if x:
            return str(x)
        LOG.error(f"OVOSApplication {self.skill_id} resource '{res_name}' for lang "
                       f"'{lang}' not found")

    def voc_match(self, utt, voc_filename, lang=None, exact=False):
        """Determine if the given utterance contains the vocabulary provided.

        By default the method checks if the utterance contains the given vocab
        thereby allowing the user to say things like "yes, please" and still
        match against "Yes.voc" containing only "yes". An exact match can be
        requested.

        The method first checks in the current Skill's .voc files and secondly
        in the "res/text" folder of mycroft-core. The result is cached to
        avoid hitting the disk each time the method is called.

        Args:
            utt (str): Utterance to be tested
            voc_filename (str): Name of vocabulary file (e.g. 'yes' for
                                'res/text/en-us/yes.voc')
            lang (str): Language code, defaults to self.lang
            exact (bool): Whether the vocab must exactly match the utterance

        Returns:
            bool: True if the utterance has the given vocabulary it
        """
        lang = lang or self.lang
        cache_key = lang + voc_filename
        if cache_key not in self.voc_match_cache:
            # Check for both skill resources and mycroft-core resources
            voc = self.find_resource(voc_filename + '.voc', 'vocab')
            if not voc:  # Check for vocab in mycroft/ovos core resources
                voc = resolve_resource_file(join('text', lang,
                                                 voc_filename + '.voc')) or \
                      resolve_ovos_resource_file(join('text', lang,
                                                      voc_filename + '.voc'))

            if not voc or not exists(voc):
                LOG.warning('Could not find {}.voc file'.format(voc_filename))
                return False
            # load vocab and flatten into a simple list
            vocab = read_vocab_file(voc)
            self.voc_match_cache[cache_key] = list(chain(*vocab))
        if utt:
            if exact:
                # Check for exact match
                return any(i.strip() == utt
                           for i in self.voc_match_cache[cache_key])
            else:
                # Check for matches against complete words
                return any([re.match(r'.*\b' + i + r'\b.*', utt)
                            for i in self.voc_match_cache[cache_key]])
        else:
            return False

    def remove_voc(self, utt, voc_filename, lang=None):
        """ removes any entry in .voc file from the utterance """
        lang = lang or self.lang
        cache_key = lang + voc_filename

        if cache_key not in self.voc_match_cache:
            self.voc_match(utt, voc_filename, lang)

        if utt:
            # Check for matches against complete words
            for i in self.voc_match_cache.get(cache_key) or []:
                # Substitute only whole words matching the token
                utt = re.sub(r'\b' + i + r"\b", "", utt)

        return utt

    # speech
    @property
    def dialog_renderer(self):
        return self.resources.dialog_renderer

    def speak(self, utterance, expect_response=False, wait=True, meta=None):
        """Speak a sentence.

        Args:
            utterance (str):        sentence mycroft should speak
            expect_response (bool): set to True if Mycroft should listen
                                    for a response immediately after
                                    speaking the utterance.
            wait (bool):            set to True to block while the text
                                    is being spoken.
            meta:                   Information of what built the sentence.
        """
        # registers the skill as being active
        meta = meta or {}
        meta['skill'] = self.skill_id
        data = {'utterance': utterance,
                'expect_response': expect_response,
                'meta': meta,
                'lang': self.lang}
        message = dig_for_message()
        m = message.forward("speak", data) if message \
            else Message("speak", data)
        m.context["skill_id"] = self.skill_id
        self.bus.emit(m)
        if wait:
            wait_while_speaking()

    def speak_dialog(self, key, data=None, expect_response=False, wait=True):
        """ Speak a random sentence from a dialog file.

        Args:
            key (str): dialog file key (e.g. "hello" to speak from the file
                                        "locale/en-us/hello.dialog")
            data (dict): information used to populate sentence
            expect_response (bool): set to True if Mycroft should listen
                                    for a response immediately after
                                    speaking the utterance.
            wait (bool):            set to True to block while the text
                                    is being spoken.
        """
        if self.dialog_renderer:
            data = data or {}
            self.speak(
                self.dialog_renderer.render(key, data),
                expect_response, wait, meta={'dialog': key, 'data': data}
            )
        else:
            LOG.warning(
                'dialog_render is None, does the locale/dialog folder exist?'
            )
            self.speak(key, expect_response, wait, {})

    # continuous dialog
    def make_active(self):
        """Bump skill to active_skill list in intent_service.

        This enables converse method to be called even without skill being
        used in last 5 minutes.
        """
        msg = dig_for_message() or Message("")
        if "skill_id" not in msg.context:
            msg.context["skill_id"] = self.skill_id
        self.bus.emit(msg.forward('active_skill_request',
                                  {'skill_id': self.skill_id}))

    def converse(self, message=None):
        """Handle conversation.

        This method gets a peek at utterances before the normal intent
        handling process after a skill has been invoked once.

        To use, override the converse() method and return True to
        indicate that the utterance has been handled.

        utterances and lang are depreciated

        Args:
            message:    a message object containing a message type with an
                        optional JSON data packet

        Returns:
            bool: True if an utterance was handled, otherwise False
        """
        return False

    def get_response(self, dialog='', data=None, validator=None,
                     on_fail=None, num_retries=-1):
        """Get response from user.

        If a dialog is supplied it is spoken, followed immediately by listening
        for a user response. If the dialog is omitted listening is started
        directly.

        The response can optionally be validated before returning.

        Example::

            color = self.get_response('ask.favorite.color')

        Args:
            dialog (str): Optional dialog to speak to the user
            data (dict): Data used to render the dialog
            validator (any): Function with following signature::

                def validator(utterance):
                    return utterance != "red"

            on_fail (any):
                Dialog or function returning literal string to speak on
                invalid input. For example::

                    def on_fail(utterance):
                        return "nobody likes the color red, pick another"

            num_retries (int): Times to ask user for input, -1 for infinite
                NOTE: User can not respond and timeout or say "cancel" to stop

        Returns:
            str: User's reply or None if timed out or canceled
        """
        data = data or {}

        def on_fail_default(utterance):
            fail_data = data.copy()
            fail_data['utterance'] = utterance
            if on_fail:
                if self.dialog_renderer:
                    return self.dialog_renderer.render(on_fail, fail_data)
                return on_fail
            else:
                if self.dialog_renderer:
                    return self.dialog_renderer.render(dialog, data)
                return dialog

        def is_cancel(utterance):
            return self.voc_match(utterance, 'cancel')

        def validator_default(utterance):
            # accept anything except 'cancel'
            return not is_cancel(utterance)

        on_fail_fn = on_fail if callable(on_fail) else on_fail_default
        validator = validator or validator_default

        # Speak query and wait for user response
        if dialog:
            self.speak_dialog(dialog, data, expect_response=True, wait=True)
        else:
            msg = dig_for_message()
            msg = msg.reply('mycroft.mic.listen') if msg else \
                Message('mycroft.mic.listen',
                        context={"skill_id": self.skill_id})
            self.bus.emit(msg)
        return self._wait_response(is_cancel, validator, on_fail_fn,
                                   num_retries)

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
                    LOG.debug("get_response aborted")
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

    def ask_yesno(self, prompt, data=None):
        """Read prompt and wait for a yes/no answer

        This automatically deals with translation and common variants,
        such as 'yeah', 'sure', etc.

        Args:
              prompt (str): a dialog id or string to read
              data (dict): response data
        Returns:
              string:  'yes', 'no' or whatever the user response if not
                       one of those, including None
        """
        resp = self.get_response(dialog=prompt, data=data)

        if self.voc_match(resp, 'yes'):
            return 'yes'
        elif self.voc_match(resp, 'no'):
            return 'no'
        else:
            return resp

    def ask_selection(self, options, dialog='',
                      data=None, min_conf=0.65, numeric=False):
        """Read options, ask dialog question and wait for an answer.

        This automatically deals with fuzzy matching and selection by number
        e.g.

        * "first option"
        * "last option"
        * "second option"
        * "option number four"

        Args:
              options (list): list of options to present user
              dialog (str): a dialog id or string to read AFTER all options
              data (dict): Data used to render the dialog
              min_conf (float): minimum confidence for fuzzy match, if not
                                reached return None
              numeric (bool): speak options as a numeric menu
        Returns:
              string: list element selected by user, or None
        """
        assert isinstance(options, list)

        if not len(options):
            return None
        elif len(options) == 1:
            return options[0]

        if numeric:
            for idx, opt in enumerate(options):
                opt_str = "{number}, {option_text}".format(
                    number=pronounce_number(
                        idx + 1, self.lang), option_text=opt)

                self.speak(opt_str, wait=True)
        else:
            opt_str = join_list(options, "or", lang=self.lang) + "?"
            self.speak(opt_str, wait=True)

        resp = self.get_response(dialog=dialog, data=data)

        if resp:
            match, score = match_one(resp, options)
            if score < min_conf:
                if self.voc_match(resp, 'last'):
                    resp = options[-1]
                else:
                    num = extract_number(resp, ordinals=True, lang=self.lang)
                    resp = None
                    if num and num <= len(options):
                        resp = options[num - 1]
            else:
                resp = match
        return resp

    # intents
    def _register_decorated(self):
        """Register all intent handlers that are decorated with an intent.

        Looks for all functions that have been marked by a decorator
        and read the intent data from them.  The intent handlers aren't the
        only decorators used.  Skip properties as calling getattr on them
        executes the code which may have unintended side-effects
        """
        for attr_name in get_non_properties(self):
            method = getattr(self, attr_name)
            if hasattr(method, 'intents'):
                for intent in getattr(method, 'intents'):
                    self.register_intent(intent, method)

            if hasattr(method, 'intent_files'):
                for intent_file in getattr(method, 'intent_files'):
                    self.register_intent_file(intent_file, method)

            if hasattr(method, 'intent_layers'):
                for layer_name, intent_files in \
                        getattr(method, 'intent_layers').items():
                    self.register_intent_layer(layer_name, intent_files)

            # TODO support for multiple converse handlers (?)
            if hasattr(method, 'converse'):
                self.converse = method
        self.register_resting_screen()

    def register_intent_layer(self, layer_name, intent_list):
        for intent_file in intent_list:
            if IntentBuilder is not None and isinstance(intent_file, IntentBuilder):
                intent = intent_file.build()
                name = intent.name
            elif Intent is not None and isinstance(intent_file, Intent):
                name = intent_file.name
            else:
                name = f'{self.skill_id}:{intent_file}'
            self.intent_layers.update_layer(layer_name, [name])

    def _register_adapt_intent(self, intent_parser, handler):
        """Register an adapt intent.

        Will handle registration of anonymous
        Args:
            intent_parser: Intent object to parse utterance for the handler.
            handler (func): function to register with intent
        """
        # Default to the handler's function name if none given
        is_anonymous = not intent_parser.name
        name = intent_parser.name or handler.__name__
        if is_anonymous:
            # Find a good name
            original_name = name
            nbr = 0
            while name in self.intent_service:
                nbr += 1
                name = f'{original_name}{nbr}'
        else:
            if name in self.intent_service:
                raise ValueError(f'The intent name {name} is already taken')

        munge_intent_parser(intent_parser, name, self.skill_id)
        self.intent_service.register_adapt_intent(name, intent_parser)
        if handler:
            self.add_event(intent_parser.name, handler,
                           'mycroft.skill.handler')

    def register_vocabulary(self, entity, entity_type, lang=None):
        """ Register a word to a keyword

        Args:
            entity:         word to register
            entity_type:    Intent handler entity to tie the word to
        """
        msg = dig_for_message() or Message("")
        if "skill_id" not in msg.context:
            msg.context["skill_id"] = self.skill_id
        self.bus.emit(msg.forward('register_vocab', {
            'start': entity,
            'end': to_alnum(self.skill_id) + entity_type,
            'lang': lang or self.lang}))

    def register_regex(self, regex_str, lang=None):
        """Register a new regex.
        Args:
            regex_str: Regex string
        """
        LOG.debug('registering regex string: ' + regex_str)
        regex = munge_regex(regex_str, self.skill_id)
        re.compile(regex)  # validate regex
        self.intent_service.register_adapt_regex(regex, lang=lang or self.lang)

    def register_intent(self, intent_parser, handler):
        """Register an Intent with the intent service.

        Args:
            intent_parser: Intent, IntentBuilder object or padatious intent
                           file to parse utterance for the handler.
            handler (func): function to register with intent
        """
        if IntentBuilder is not None and isinstance(intent_parser, IntentBuilder):
            intent_parser = intent_parser.build()
        if (isinstance(intent_parser, str) and
                intent_parser.endswith('.intent')):
            return self.register_intent_file(intent_parser, handler)
        elif not Intent or not isinstance(intent_parser, Intent):
            raise ValueError('"' + str(intent_parser) + '" is not an Intent')

        return self._register_adapt_intent(intent_parser, handler)

    def clear_intents(self):
        # remove bus handlers, otherwise if re-registered we get multiple
        # handler executions
        for intent_name, _ in self.intent_service:
            event_name = f'{self.skill_id}:{intent_name}'
            self.remove_event(event_name)

        self.intent_service.detach_all()  # delete old intents before re-registering

    def register_intent_file(self, intent_file, handler):
        """Register an Intent file with the intent service.

        For example:

        === food.order.intent ===
        Order some {food}.
        Order some {food} from {place}.
        I'm hungry.
        Grab some {food} from {place}.

        Optionally, you can also use <register_entity_file>
        to specify some examples of {food} and {place}

        In addition, instead of writing out multiple variations
        of the same sentence you can write:

        === food.order.intent ===
        (Order | Grab) some {food} (from {place} | ).
        I'm hungry.

        Args:
            intent_file: name of file that contains example queries
                         that should activate the intent.  Must end with
                         '.intent'
            handler:     function to register with intent
        """
        langs = [self._core_lang] + self.secondary_langs
        for lang in langs:
            name = f'{self.skill_id}:{intent_file}'
            filename = self.find_resource(intent_file, 'vocab', lang=lang)
            if not filename:
                LOG.error('Unable to find "{}"'.format(intent_file))
                continue
            self.intent_service.register_padatious_intent(name, filename, lang)
            if handler:
                self.add_event(name, handler, 'mycroft.skill.handler')

    def register_entity_file(self, entity_file):
        """Register an Entity file with the intent service.

        An Entity file lists the exact values that an entity can hold.
        For example:

        === ask.day.intent ===
        Is it {weekend}?

        === weekend.entity ===
        Saturday
        Sunday

        Args:
            entity_file (string): name of file that contains examples of an
                                  entity.  Must end with '.entity'
        """
        if entity_file.endswith('.entity'):
            entity_file = entity_file.replace('.entity', '')
        langs = [self._core_lang] + self.secondary_langs
        for lang in langs:
            filename = self.find_resource(entity_file + ".entity", 'vocab',
                                          lang=lang)
            if not filename:
                LOG.error(f'Unable to find "{entity_file}"')
                continue
            name = '{}:{}'.format(self.skill_id, entity_file)
            self.intent_service.register_padatious_entity(name, filename, lang)

    def _handle_enable_intent(self, message):
        """Listener to enable a registered intent if it belongs to this skill.
        """
        intent_name = message.data['intent_name']
        for (name, _) in self.intent_service.detached_intents:
            if name == intent_name:
                return self.enable_intent(intent_name)

    def _handle_disable_intent(self, message):
        """Listener to disable a registered intent if it belongs to this skill.
        """
        intent_name = message.data['intent_name']
        for (name, _) in self.intent_service:
            if name == intent_name:
                return self.disable_intent(intent_name)

    def disable_intent(self, intent_name):
        """Disable a registered intent if it belongs to this skill.

        Args:
            intent_name (string): name of the intent to be disabled

        Returns:
                bool: True if disabled, False if it wasn't registered
        """
        if intent_name in self.intent_service:
            LOG.info('Disabling intent ' + intent_name)
            name = f'{self.skill_id}:{intent_name}'
            self.intent_service.detach_intent(name)

            langs = [self._core_lang] + self.secondary_langs
            for lang in langs:
                lang_intent_name = f'{name}_{lang}'
                self.intent_service.detach_intent(lang_intent_name)
            return True
        else:
            LOG.error('Could not disable '
                      '{}, it hasn\'t been registered.'.format(intent_name))
            return False

    def enable_intent(self, intent_name):
        """(Re)Enable a registered intent if it belongs to this skill.

        Args:
            intent_name: name of the intent to be enabled

        Returns:
            bool: True if enabled, False if it wasn't registered
        """
        intent = self.intent_service.get_intent(intent_name)
        if intent:
            if ".intent" in intent_name:
                self.register_intent_file(intent_name, None)
            else:
                intent.name = intent_name
                self.register_intent(intent, None)
            LOG.debug('Enabling intent {}'.format(intent_name))
            return True
        else:
            LOG.error('Could not enable '
                      '{}, it hasn\'t been registered.'.format(intent_name))
            return False

    def set_context(self, context, word='', origin=''):
        """Add context to intent service

        Args:
            context:    Keyword
            word:       word connected to keyword
            origin:     origin of context
        """
        if not isinstance(context, str):
            raise ValueError('Context should be a string')
        if not isinstance(word, str):
            raise ValueError('Word should be a string')

        context = to_alnum(self.skill_id) + context
        self.intent_service.set_adapt_context(context, word, origin)

    def remove_context(self, context):
        """Remove a keyword from the context manager."""
        if not isinstance(context, str):
            raise ValueError('context should be a string')
        context = to_alnum(self.skill_id) + context
        self.intent_service.remove_adapt_context(context)

    def _handle_set_cross_context(self, message):
        """Add global context to intent service."""
        context = message.data.get('context')
        word = message.data.get('word')
        origin = message.data.get('origin')

        self.set_context(context, word, origin)

    def _handle_remove_cross_context(self, message):
        """Remove global context from intent service."""
        context = message.data.get('context')
        self.remove_context(context)

    def set_cross_context(self, context, word=''):
        """Tell all skills to add a context to intent service

        Args:
            context:    Keyword
            word:       word connected to keyword
        """
        msg = dig_for_message() or Message("")
        if "skill_id" not in msg.context:
            msg.context["skill_id"] = self.skill_id
        self.bus.emit(msg.forward('mycroft.skill.set_cross_context',
                                  {'context': context, 'word': word,
                                   'origin': self.skill_id}))

    def remove_cross_context(self, context):
        """Tell all skills to remove a keyword from the context manager."""
        if not isinstance(context, str):
            raise ValueError('context should be a string')
        msg = dig_for_message() or Message("")
        if "skill_id" not in msg.context:
            msg.context["skill_id"] = self.skill_id
        self.bus.emit(msg.forward('mycroft.skill.remove_cross_context',
                                  {'context': context}))

    def register_resting_screen(self):
        """Registers resting screen from the resting_screen_handler decorator.

        This only allows one screen and if two is registered only one
        will be used.
        """
        for attr_name in get_non_properties(self):
            method = getattr(self, attr_name)
            if hasattr(method, 'resting_handler'):
                self.resting_name = method.resting_handler
                LOG.info('Registering resting screen {} for {}.'.format(
                    method, self.resting_name))

                # Register for handling resting screen
                msg_type = '{}.{}'.format(self.skill_id, 'idle')
                self.add_event(msg_type, method)
                # Register handler for resting screen collect message
                self.add_event('mycroft.mark2.collect_idle',
                               self._handle_collect_resting)

                # Do a send at load to make sure the skill is registered
                # if reloaded
                self._handle_collect_resting()
                break

    def _handle_collect_resting(self, message=None):
        """Handler for collect resting screen messages.

        Sends info on how to trigger this skills resting page.
        """
        LOG.info('Registering resting screen')
        msg = message or Message("")
        message = msg.reply(
            'mycroft.mark2.register_idle',
            data={'name': self.resting_name, 'id': self.skill_id},
            context={"skill_id": self.skill_id}
        )
        self.bus.emit(message)
