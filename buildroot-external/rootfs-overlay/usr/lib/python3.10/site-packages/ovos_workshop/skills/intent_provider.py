from threading import Event
from time import time as get_time, sleep
from ovos_utils.log import LOG
from ovos_utils.messagebus import Message
from ovos_workshop.skills.ovos import OVOSFallbackSkill
from ovos_config.config import read_mycroft_config, update_mycroft_config


class BaseIntentEngine:
    # TODO move to OPM
    def __init__(self, name, config=None):
        self.name = name.lower()
        config = config or read_mycroft_config()
        self.config = config.get(self.name, {})
        self.intent_samples = {}
        self.entity_samples = {}
        self.regex_samples = {}

    def add_intent(self, name, samples):
        self.intent_samples[name] = samples

    def remove_intent(self, name):
        if name in self.intent_samples:
            del self.intent_samples[name]

    def add_entity(self, name, samples):
        self.entity_samples[name] = samples

    def add_regex(self, name, pattern):
        self.regex_samples[name] = pattern

    def remove_regex(self, name):
        if name in self.regex_samples:
            del self.regex_samples[name]

    def remove_entity(self, name):
        if name in self.entity_samples:
            del self.entity_samples[name]

    def train(self, single_thread=False):
        """ train all registered intents and entities"""
        pass

    def calc_intent(self, query):
        """ return best intent for this query  """
        data = {"conf": 0,
                "utterance": query,
                "name": None}
        return data


class IntentEngineSkill(OVOSFallbackSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = None
        self.config = {}
        self.priority = 1

    def initialize(self):
        engine = BaseIntentEngine("dummy")
        self.bind_engine(engine, self.priority)

    def bind_engine(self, engine, priority=4):
        priority_skills = read_mycroft_config().get("skills", {}).get(
            "priority_skills", [])
        priority_skills.append(self.root_dir.split("/")[-1])
        update_mycroft_config({
            "skills":
                {"priority_skills": priority_skills}
        })
        self.priority = priority
        self.engine = engine
        self.config = engine.config
        self.register_messages(engine.name)
        self.register_fallback(self.handle_fallback, self.priority)
        self.finished_training_event = Event()
        self.finished_initial_train = False
        self.train_delay = self.engine.config.get('train_delay', 4)
        self.train_time = get_time() + self.train_delay

    def register_messages(self, name):
        self.bus.on('mycroft.skills.initialized', self.train)
        self.bus.on(name + ':register_intent', self._register_intent)
        self.bus.on(name + ':register_entity', self._register_entity)
        self.bus.on(name + ':register_regex', self._register_regex)

    def train(self, message=None):
        single_thread = message.data.get('single_thread', False)
        self.finished_training_event.clear()

        LOG.info('Training...')
        self.engine.train(single_thread=single_thread)
        LOG.info('Training complete.')

        self.finished_training_event.set()
        self.finished_initial_train = True

    def wait_and_train(self):
        if not self.finished_initial_train:
            return
        sleep(self.train_delay)
        if self.train_time < 0.0:
            return

        if self.train_time <= get_time() + 0.01:
            self.train_time = -1.0
            self.train()

    def _register_object(self, message, object_name, register_func):
        name = message.data['name']
        samples = message.data['samples']

        LOG.debug(
            'Registering ' + self.engine.name + ' ' + object_name + ': ' + name)

        register_func(name, samples)
        self.train_time = get_time() + self.train_delay
        self.wait_and_train()

    def register_intent(self, name, samples):
        data = {"name": name, "samples": samples}
        self._register_intent(Message(name, data))

    def register_entity(self, name, samples):
        data = {"name": name, "samples": samples}
        self._register_entity(Message(name, data))

    def register_regex(self, name, pattern):
        data = {"name": name, "pattern": pattern}
        self._register_regex(Message(name, data))

    def _register_intent(self, message):
        self._register_object(message, 'intent', self.engine.add_intent)

    def _register_entity(self, message):
        self._register_object(message, 'entity', self.engine.add_entity)

    def _register_regex(self, message):
        self._register_object(message, 'regex', self.engine.add_regex)

    def handle_fallback(self, message):
        utt = message.data.get('utterance')
        LOG.debug(self.engine.name + " fallback attempt: " + utt)

        if not self.finished_training_event.is_set():
            LOG.debug('Waiting for training to finish...')
            self.finished_training_event.wait()

        data = self.engine.calc_intent(utt)

        if data["conf"] < 0.5:
            return False

        self.make_active()

        self.bus.emit(message.reply(data["name"], data=data))
        return True
