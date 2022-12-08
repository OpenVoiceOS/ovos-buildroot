from os.path import exists, isfile


from mycroft_bus_client import MessageBusClient
from mycroft_bus_client.message import Message, dig_for_message
from ovos_utils import create_daemon
from ovos_utils.log import LOG


def to_alnum(skill_id):
    """Convert a skill id to only alphanumeric characters

     Non alpha-numeric characters are converted to "_"

    Args:
        skill_id (str): identifier to be converted
    Returns:
        (str) String of letters
    """
    return ''.join(c if c.isalnum() else '_' for c in str(skill_id))


def munge_regex(regex, skill_id):
    """Insert skill id as letters into match groups.

    Args:
        regex (str): regex string
        skill_id (str): skill identifier
    Returns:
        (str) munged regex
    """
    base = '(?P<' + to_alnum(skill_id)
    return base.join(regex.split('(?P<'))


def munge_intent_parser(intent_parser, name, skill_id):
    """Rename intent keywords to make them skill exclusive
    This gives the intent parser an exclusive name in the
    format <skill_id>:<name>.  The keywords are given unique
    names in the format <Skill id as letters><Intent name>.

    The function will not munge instances that's already been
    munged

    Args:
        intent_parser: (IntentParser) object to update
        name: (str) Skill name
        skill_id: (int) skill identifier
    """
    # Munge parser name
    if not name.startswith(str(skill_id) + ':'):
        intent_parser.name = str(skill_id) + ':' + name
    else:
        intent_parser.name = name

    # Munge keywords
    skill_id = to_alnum(skill_id)
    # Munge required keyword
    reqs = []
    for i in intent_parser.requires:
        if not i[0].startswith(skill_id):
            kw = (skill_id + i[0], skill_id + i[0])
            reqs.append(kw)
        else:
            reqs.append(i)
    intent_parser.requires = reqs

    # Munge optional keywords
    opts = []
    for i in intent_parser.optional:
        if not i[0].startswith(skill_id):
            kw = (skill_id + i[0], skill_id + i[0])
            opts.append(kw)
        else:
            opts.append(i)
    intent_parser.optional = opts

    # Munge at_least_one keywords
    at_least_one = []
    for i in intent_parser.at_least_one:
        element = [skill_id + e.replace(skill_id, '') for e in i]
        at_least_one.append(tuple(element))
    intent_parser.at_least_one = at_least_one


class IntentServiceInterface:
    """Interface to communicate with the Mycroft intent service.

    This class wraps the messagebus interface of the intent service allowing
    for easier interaction with the service. It wraps both the Adapt and
    Padatious parts of the intent services.
    """

    def __init__(self, bus=None):
        self.bus = bus
        self.skill_id = self.__class__.__name__
        self.registered_intents = []
        self.detached_intents = []

    def set_bus(self, bus):
        self.bus = bus

    def set_id(self, skill_id):
        self.skill_id = skill_id

    def register_adapt_keyword(self, vocab_type, entity, aliases=None,
                               lang=None):
        """Send a message to the intent service to add an Adapt keyword.

            vocab_type(str): Keyword reference
            entity (str): Primary keyword
            aliases (list): List of alternative kewords
        """
        aliases = aliases or []
        msg = dig_for_message() or Message("")
        if "skill_id" not in msg.context:
            msg.context["skill_id"] = self.skill_id
        self.bus.emit(msg.forward("register_vocab",
                                  {'start': entity,
                                   'end': vocab_type,
                                   'lang': lang}))
        for alias in aliases:
            self.bus.emit(msg.forward("register_vocab",
                                      {'start': alias,
                                       'end': vocab_type,
                                       'alias_of': entity,
                                       'lang': lang}))

    def register_adapt_regex(self, regex, lang=None):
        """Register a regex with the intent service.

        Args:
            regex (str): Regex to be registered, (Adapt extracts keyword
                         reference from named match group.
        """
        msg = dig_for_message() or Message("")
        if "skill_id" not in msg.context:
            msg.context["skill_id"] = self.skill_id
        self.bus.emit(msg.forward("register_vocab",
                                  {'regex': regex, 'lang': lang}))

    def register_adapt_intent(self, name, intent_parser):
        """Register an Adapt intent parser object.

        Serializes the intent_parser and sends it over the messagebus to
        registered.
        """
        msg = dig_for_message() or Message("")
        if "skill_id" not in msg.context:
            msg.context["skill_id"] = self.skill_id
        self.bus.emit(msg.forward("register_intent", intent_parser.__dict__))
        self.registered_intents.append((name, intent_parser))
        self.detached_intents = [detached for detached in self.detached_intents
                                 if detached[0] != name]

    def detach_intent(self, intent_name):
        """Remove an intent from the intent service.

        The intent is saved in the list of detached intents for use when
        re-enabling an intent.

        Args:
            intent_name(str): Intent reference
        """
        # split skill_id if needed
        if intent_name not in self and ":" in intent_name:
            name = intent_name.split(':')[1]
        else:
            name = intent_name

        if name in self:
            msg = dig_for_message() or Message("")
            if "skill_id" not in msg.context:
                msg.context["skill_id"] = self.skill_id
            self.bus.emit(msg.forward("detach_intent",
                                      {"intent_name": intent_name}))
            self.detached_intents.append((name, self.get_intent(name)))
            self.registered_intents = [pair for pair in self.registered_intents
                                       if pair[0] != name]

    def set_adapt_context(self, context, word, origin):
        """Set an Adapt context.

        Args:
            context (str): context keyword name
            word (str): word to register
            origin (str): original origin of the context (for cross context)
        """
        msg = dig_for_message() or Message("")
        if "skill_id" not in msg.context:
            msg.context["skill_id"] = self.skill_id
        self.bus.emit(msg.forward('add_context',
                                  {'context': context, 'word': word,
                                   'origin': origin}))

    def remove_adapt_context(self, context):
        """Remove an active Adapt context.

        Args:
            context(str): name of context to remove
        """
        msg = dig_for_message() or Message("")
        if "skill_id" not in msg.context:
            msg.context["skill_id"] = self.skill_id
        self.bus.emit(msg.forward('remove_context', {'context': context}))

    def register_padatious_intent(self, intent_name, filename, lang):
        """Register a padatious intent file with Padatious.

        Args:
            intent_name(str): intent identifier
            filename(str): complete file path for entity file
        """
        if not isinstance(filename, str):
            raise ValueError('Filename path must be a string')
        if not exists(filename):
            raise FileNotFoundError('Unable to find "{}"'.format(filename))

        data = {'file_name': filename,
                'name': intent_name,
                'lang': lang}
        msg = dig_for_message() or Message("")
        if "skill_id" not in msg.context:
            msg.context["skill_id"] = self.skill_id
        self.bus.emit(msg.forward("padatious:register_intent", data))
        self.registered_intents.append((intent_name.split(':')[-1], data))

    def register_padatious_entity(self, entity_name, filename, lang):
        """Register a padatious entity file with Padatious.

        Args:
            entity_name(str): entity name
            filename(str): complete file path for entity file
        """
        if not isinstance(filename, str):
            raise ValueError('Filename path must be a string')
        if not exists(filename):
            raise FileNotFoundError('Unable to find "{}"'.format(filename))
        msg = dig_for_message() or Message("")
        if "skill_id" not in msg.context:
            msg.context["skill_id"] = self.skill_id
        self.bus.emit(msg.forward('padatious:register_entity',
                                  {'file_name': filename,
                                   'name': entity_name,
                                   'lang': lang}))

    def __iter__(self):
        """Iterator over the registered intents.

        Returns an iterator returning name-handler pairs of the registered
        intent handlers.
        """
        return iter(self.registered_intents)

    def __contains__(self, val):
        """Checks if an intent name has been registered."""
        return val in [i[0] for i in self.registered_intents]

    def get_intent_names(self):
        return [i[0] for i in self.registered_intents]

    def detach_all(self):
        for name in self.get_intent_names():
            self.detach_intent(name)
        self.registered_intents = []
        self.detached_intents = []

    def get_intent(self, intent_name):
        """Get intent from intent_name.

        This will find both enabled and disabled intents.

        Args:
            intent_name (str): name to find.

        Returns:
            Found intent or None if none were found.
        """
        for name, intent in self:
            if name == intent_name:
                return intent
        for name, intent in self.detached_intents:
            if name == intent_name:
                return intent
        return None


class IntentQueryApi:
    """
    Query Intent Service at runtime
    """

    def __init__(self, bus=None, timeout=5):
        if bus is None:
            bus = MessageBusClient()
            create_daemon(bus.run_forever)
        self.bus = bus
        self.timeout = timeout

    def get_adapt_intent(self, utterance, lang="en-us"):
        """ get best adapt intent for utterance """
        msg = Message("intent.service.adapt.get",
                      {"utterance": utterance, "lang": lang},
                      context={"destination": "intent_service",
                               "source": "intent_api"})

        resp = self.bus.wait_for_response(msg,
                                          'intent.service.adapt.reply',
                                          timeout=self.timeout)
        data = resp.data if resp is not None else {}
        if not data:
            LOG.error("Intent Service timed out!")
            return None
        return data["intent"]

    def get_padatious_intent(self, utterance, lang="en-us"):
        """ get best padatious intent for utterance """
        msg = Message("intent.service.padatious.get",
                      {"utterance": utterance, "lang": lang},
                      context={"destination": "intent_service",
                               "source": "intent_api"})
        resp = self.bus.wait_for_response(msg,
                                          'intent.service.padatious.reply',
                                          timeout=self.timeout)
        data = resp.data if resp is not None else {}
        if not data:
            LOG.error("Intent Service timed out!")
            return None
        return data["intent"]

    def get_intent(self, utterance, lang="en-us"):
        """ get best intent for utterance """
        msg = Message("intent.service.intent.get",
                      {"utterance": utterance, "lang": lang},
                      context={"destination": "intent_service",
                               "source": "intent_api"})
        resp = self.bus.wait_for_response(msg,
                                          'intent.service.intent.reply',
                                          timeout=self.timeout)
        data = resp.data if resp is not None else {}
        if not data:
            LOG.error("Intent Service timed out!")
            return None
        return data["intent"]

    def get_skill(self, utterance, lang="en-us"):
        """ get skill that utterance will trigger """
        intent = self.get_intent(utterance, lang)
        if not intent:
            return None
        # theoretically skill_id might be missing
        if intent.get("skill_id"):
            return intent["skill_id"]
        # retrieve skill from munged intent name
        if intent.get("intent_name"):  # padatious + adapt
            return intent["name"].split(":")[0]
        if intent.get("intent_type"):  # adapt
            return intent["intent_type"].split(":")[0]
        return None  # raise some error here maybe? this should never happen

    def get_skills_manifest(self):
        msg = Message("intent.service.skills.get",
                      context={"destination": "intent_service",
                               "source": "intent_api"})
        resp = self.bus.wait_for_response(msg,
                                          'intent.service.skills.reply',
                                          timeout=self.timeout)
        data = resp.data if resp is not None else {}
        if not data:
            LOG.error("Intent Service timed out!")
            return None
        return data["skills"]

    def get_active_skills(self, include_timestamps=False):
        msg = Message("intent.service.active_skills.get",
                      context={"destination": "intent_service",
                               "source": "intent_api"})
        resp = self.bus.wait_for_response(msg,
                                          'intent.service.active_skills.reply',
                                          timeout=self.timeout)
        data = resp.data if resp is not None else {}
        if not data:
            LOG.error("Intent Service timed out!")
            return None
        if include_timestamps:
            return data["skills"]
        return [s[0] for s in data["skills"]]

    def get_adapt_manifest(self):
        msg = Message("intent.service.adapt.manifest.get",
                      context={"destination": "intent_service",
                               "source": "intent_api"})
        resp = self.bus.wait_for_response(msg,
                                          'intent.service.adapt.manifest',
                                          timeout=self.timeout)
        data = resp.data if resp is not None else {}
        if not data:
            LOG.error("Intent Service timed out!")
            return None
        return data["intents"]

    def get_padatious_manifest(self):
        msg = Message("intent.service.padatious.manifest.get",
                      context={"destination": "intent_service",
                               "source": "intent_api"})
        resp = self.bus.wait_for_response(msg,
                                          'intent.service.padatious.manifest',
                                          timeout=self.timeout)
        data = resp.data if resp is not None else {}
        if not data:
            LOG.error("Intent Service timed out!")
            return None
        return data["intents"]

    def get_intent_manifest(self):
        padatious = self.get_padatious_manifest()
        adapt = self.get_adapt_manifest()
        return {"adapt": adapt,
                "padatious": padatious}

    def get_vocab_manifest(self):
        msg = Message("intent.service.adapt.vocab.manifest.get",
                      context={"destination": "intent_service",
                               "source": "intent_api"})
        reply_msg_type = 'intent.service.adapt.vocab.manifest'
        resp = self.bus.wait_for_response(msg,
                                          reply_msg_type,
                                          timeout=self.timeout)
        data = resp.data if resp is not None else {}
        if not data:
            LOG.error("Intent Service timed out!")
            return None

        vocab = {}
        for voc in data["vocab"]:
            if voc.get("regex"):
                continue
            if voc["end"] not in vocab:
                vocab[voc["end"]] = {"samples": []}
            vocab[voc["end"]]["samples"].append(voc["start"])
        return [{"name": voc, "samples": vocab[voc]["samples"]}
                for voc in vocab]

    def get_regex_manifest(self):
        msg = Message("intent.service.adapt.vocab.manifest.get",
                      context={"destination": "intent_service",
                               "source": "intent_api"})
        reply_msg_type = 'intent.service.adapt.vocab.manifest'
        resp = self.bus.wait_for_response(msg,
                                          reply_msg_type,
                                          timeout=self.timeout)
        data = resp.data if resp is not None else {}
        if not data:
            LOG.error("Intent Service timed out!")
            return None

        vocab = {}
        for voc in data["vocab"]:
            if not voc.get("regex"):
                continue
            name = voc["regex"].split("(?P<")[-1].split(">")[0]
            if name not in vocab:
                vocab[name] = {"samples": []}
            vocab[name]["samples"].append(voc["regex"])
        return [{"name": voc, "regexes": vocab[voc]["samples"]}
                for voc in vocab]

    def get_entities_manifest(self):
        msg = Message("intent.service.padatious.entities.manifest.get",
                      context={"destination": "intent_service",
                               "source": "intent_api"})
        reply_msg_type = 'intent.service.padatious.entities.manifest'
        resp = self.bus.wait_for_response(msg,
                                          reply_msg_type,
                                          timeout=self.timeout)
        data = resp.data if resp is not None else {}
        if not data:
            LOG.error("Intent Service timed out!")
            return None

        entities = []
        # read files
        for ent in data["entities"]:
            if isfile(ent["file_name"]):
                with open(ent["file_name"]) as f:
                    lines = f.read().replace("(", "").replace(")", "").split(
                        "\n")
                samples = []
                for l in lines:
                    samples += [a.strip() for a in l.split("|") if a.strip()]
                entities.append({"name": ent["name"], "samples": samples})
        return entities

    def get_keywords_manifest(self):
        padatious = self.get_entities_manifest()
        adapt = self.get_vocab_manifest()
        regex = self.get_regex_manifest()
        return {"adapt": adapt,
                "padatious": padatious,
                "regex": regex}


def open_intent_envelope(message):
    """Convert dictionary received over messagebus to Intent."""
    # TODO can this method be fully removed from ovos_utils ?
    from adapt.intent import Intent

    intent_dict = message.data
    return Intent(intent_dict.get('name'),
                  intent_dict.get('requires'),
                  intent_dict.get('at_least_one'),
                  intent_dict.get('optional'))
