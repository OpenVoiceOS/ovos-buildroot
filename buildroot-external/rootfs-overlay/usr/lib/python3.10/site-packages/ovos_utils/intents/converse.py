import time

from ovos_utils.intents.intent_service_interface import IntentQueryApi
from ovos_utils.log import LOG
from ovos_utils.messagebus import Message


class ConverseTracker:
    """ Using the messagebus this class recreates/keeps track of the state
    of the converse system, it uses both passive listening and active
    queries to sync it's state, it also emits 2 new bus events

    Implements https://github.com/MycroftAI/mycroft-core/pull/1468
    """
    bus = None
    active_skills = []
    converse_timeout = 5  # MAGIC NUMBER  hard coded in mycroft-core
    last_conversed = None
    intent_api = None

    @classmethod
    def connect_bus(cls, mycroft_bus):
        """Registers the bus object to use."""
        # PATCH - in mycroft-core this would be handled in intent_service
        # in here it is done in MycroftSkill.bind so i added this
        # conditional check
        if cls.bus is None and mycroft_bus is not None:
            cls.bus = mycroft_bus
            cls.intent_api = IntentQueryApi(cls.bus)
            cls.register_bus_events()

    @classmethod
    def register_bus_events(cls):
        cls.bus.on('active_skill_request', cls.handle_activate_request)
        cls.bus.on('skill.converse.response', cls.handle_converse_response)
        cls.bus.on("mycroft.skill.handler.start", cls.handle_intent_start)
        cls.bus.on("recognizer_loop:utterance", cls.handle_utterance)

    # public methods
    @classmethod
    def check_skill(cls, skill_id):
        """ Check if a skill is active """
        cls.filter_active_skills()
        for skill in list(cls.active_skills):
            if skill[0] == skill_id:
                return True
        return False

    @classmethod
    def filter_active_skills(cls):
        """ Removes expired skills from active skill list """
        # filter timestamps
        for skill in list(cls.active_skills):
            if time.time() - skill[1] <= cls.converse_timeout * 60:
                cls.remove_active_skill(skill[0])

    @classmethod
    def sync_with_intent_service(cls):
        """sync active skill list using intent api

        WARNING
            we don't have the timestamps so order might be messed up!!
            avoid calling this until
        """
        skill_ids = cls.intent_api.get_active_skills(include_timestamps=True)
        if skill_ids:
            if len(skill_ids[0]) == 2:
                # PR was merged! hurray!
                cls.active_skills = skill_ids
            else:
                # hoping they come sorted by timestamp....
                # older to newer (most recently used)
                for skill_id in reversed(skill_ids):
                    # are we tracking this skill ?
                    if not cls.check_skill(skill_id):
                        # we missed adding this skill in our tracking
                        cls.add_active_skill(skill_id)
                for skill in cls.active_skills:
                    if skill[0] not in skill_ids:
                        # we missed removing this skill in our tracking
                        cls.remove_active_skill(skill[0])

    # https://github.com/MycroftAI/mycroft-core/pull/1468
    @classmethod
    def remove_active_skill(cls, skill_id, silent=False):
        """
        Emits "converse.skill.deactivated" event, improvement of #1468
        """
        for skill in list(cls.active_skills):
            if skill[0] == skill_id:
                cls.active_skills.remove(skill)
                if not silent:
                    cls.bus.emit(Message("converse.skill.deactivated",
                                         {"skill_id": skill[0]}))

    @classmethod
    def add_active_skill(cls, skill_id):
        """
        Emits "converse.skill.activated" event, improvement of #1468
        """
        # search the list for an existing entry that already contains it
        # and remove that reference
        if skill_id != '':
            cls.remove_active_skill(skill_id, silent=True)
            # add skill with timestamp to start of skill_list
            cls.active_skills.insert(0, [skill_id, time.time()])
            # this might be sent more than once and it's perfectly fine
            # it's just a new info message not consumed anywhere by default
            cls.bus.emit(Message("converse.skill.activated",
                                 {"skill_id": skill_id}))
        else:
            LOG.warning('Skill ID was empty, won\'t add to list of '
                        'active skills.')

    # status tracking
    @classmethod
    def handle_activate_request(cls, message):
        """
        a skill bumped itself to the top of active skills list
        duplicate functionality from mycroft-core, keeping list in sync
        """
        skill_id = message.data["skill_id"]
        cls.add_active_skill(skill_id)

    @classmethod
    def handle_converse_error(cls, message):
        """
        a skill was removed from active skill list due to converse error
        duplicate functionality from mycroft-core, keeping list in sync
        """
        skill_id = message.data["skill_id"]
        if message.data["error"] == "skill id does not exist":
            cls.remove_active_skill(skill_id)

    @classmethod
    def handle_intent_start(cls, message):
        """
        duplicate functionality from mycroft-core, keeping list in sync

        TODO skill_id from message, core is not passing it along... it used
        to be possible to retrieve it from munged message but that changed.
        send a PR (if those got merged this code wouldn't exist)

        handle_utterance will take over this functionality for now
        handle_converse_response will take corrective action
        """
        # skill_id = message.data["skill_id"]
        # bump skill to top of active list
        # cls.add_active_skill(skill_id)

    @classmethod
    def handle_utterance(cls, message):
        """
        duplicate functionality from mycroft-core, keeping list in sync

        WORKAROUND - skill_id missing in handle_intent_start, will keep list
        in sync by using the IntentAPI to check what skill the utterance
        should trigger

        handle_converse_response will take corrective action
        """
        # NOTE borked in mycroft-core
        # needs https://github.com/MycroftAI/mycroft-core/pull/2786
        skill_id = cls.intent_api.get_skill(message.data["utterances"][0])
        if skill_id:
            # this skill will trigger and therefore is the last active skill
            cls.add_active_skill(skill_id)
        # will remove expired intents from list
        cls.filter_active_skills()

    @classmethod
    def handle_converse_response(cls, message):
        """
        tracks last_conversed skill

        FAILSAFE - additional checks to correct active skills list,
        but that should never happen, accounts for mistakes in
        handle_utterance / intent_api

        accounts for https://github.com/MycroftAI/mycroft-core/pull/2786
        not yet being merged
        """
        skill_id = message.data["skill_id"]
        if 'error' in message.data:
            cls.handle_converse_error(message)
        elif message.data.get('result') is True:
            cls.last_conversed = skill_id
            if not cls.check_skill(skill_id):
                # seems like we missed adding this skill to active list
                # NOTE this is a failsafe and should never trigger
                # since this answered True we have the real timestamp
                cls.add_active_skill(skill_id)
        elif not cls.check_skill(skill_id):
            # seems like we missed adding this skill to active list
            # NOTE this is a failsafe and should never trigger
            # since this answered false and we don't have the real timestamp
            # let's add it to the end of the active_skills list
            ts = time.time()
            if len(cls.active_skills):
                ts = cls.active_skills[-1][1]
            cls.active_skills.append([skill_id, ts])
