import enum


class UtteranceTask(enum.IntEnum):
    """ A task is a user facing category
    It is used in configuration files to assign preference to a plugin
    when more than one solve the same problem
    TRANSFORM, ADD_CONTEXT and OTHER are used as default values
    """
    TRANSFORM = enum.auto()
    ADD_CONTEXT = enum.auto()
    OTHER = enum.auto()
    POSTAG = enum.auto()
    NER = enum.auto()
    KEYWORD_EXTRACTION = enum.auto()
    TOPIC_EXTRACTION = enum.auto()
    COREFERENCE_RESOLUTION = enum.auto()
    TRANSLATION = enum.auto()
    CLASSIFY_QUESTION = enum.auto()


class AudioTask(enum.IntEnum):
    """ A task is a user facing category
    It is used in configuration files to assign preference to a plugin
    when more than one solve the same problem
    TRANSFORM, ADD_CONTEXT and OTHER are used as default values
    """
    TRANSFORM = enum.auto()
    ADD_CONTEXT = enum.auto()
    OTHER = enum.auto()
    REMOVE_NOISE = enum.auto()
    TRIM_SILENCE = enum.auto()
