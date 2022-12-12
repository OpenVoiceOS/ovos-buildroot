from ovos_utils.intents.intent_service_interface import IntentQueryApi, \
    IntentServiceInterface
from ovos_utils.intents.converse import ConverseTracker
from ovos_utils.intents.layers import IntentLayers

try:
    from adapt.intent import IntentBuilder, Intent
except ImportError:
    # adapt is optional, these classes are mainly syntactic sugar

    class Intent:
        def __init__(self, name, requires, at_least_one, optional):
            """Create Intent object
            Args:
                name(str): Name for Intent
                requires(list): Entities that are required
                at_least_one(list): One of these Entities are required
                optional(list): Optional Entities used by the intent
            """
            self.name = name
            self.requires = requires
            self.at_least_one = at_least_one
            self.optional = optional

        def validate(self, tags, confidence):
            """Using this method removes tags from the result of validate_with_tags
            Returns:
                intent(intent): Results from validate_with_tags
            """
            raise NotImplementedError("please install adapt-parser")

        def validate_with_tags(self, tags, confidence):
            """Validate whether tags has required entites for this intent to fire
            Args:
                tags(list): Tags and Entities used for validation
                confidence(float): The weight associate to the parse result,
                    as indicated by the parser. This is influenced by a parser
                    that uses edit distance or context.
            Returns:
                intent, tags: Returns intent and tags used by the intent on
                    failure to meat required entities then returns intent with
                    confidence
                    of 0.0 and an empty list for tags.
            """
            raise NotImplementedError("please install adapt-parser")


    class IntentBuilder:
        """
        IntentBuilder, used to construct intent parsers.
        Attributes:
            at_least_one(list): A list of Entities where one is required.
                These are separated into lists so you can have one of (A or B) and
                then require one of (D or F).
            requires(list): A list of Required Entities
            optional(list): A list of optional Entities
            name(str): Name of intent
        Notes:
            This is designed to allow construction of intents in one line.
        Example:
            IntentBuilder("Intent")\
                .requires("A")\
                .one_of("C","D")\
                .optional("G").build()
        """

        def __init__(self, intent_name):
            """
            Constructor
            Args:
                intent_name(str): the name of the intents that this parser
                parses/validates
            """
            self.at_least_one = []
            self.requires = []
            self.optional = []
            self.name = intent_name

        def one_of(self, *args):
            """
            The intent parser should require one of the provided entity types to
            validate this clause.
            Args:
                args(args): *args notation list of entity names
            Returns:
                self: to continue modifications.
            """
            self.at_least_one.append(args)
            return self

        def require(self, entity_type, attribute_name=None):
            """
            The intent parser should require an entity of the provided type.
            Args:
                entity_type(str): an entity type
                attribute_name(str): the name of the attribute on the parsed intent.
                Defaults to match entity_type.
            Returns:
                self: to continue modifications.
            """
            if not attribute_name:
                attribute_name = entity_type
            self.requires += [(entity_type, attribute_name)]
            return self

        def optionally(self, entity_type, attribute_name=None):
            """
            Parsed intents from this parser can optionally include an entity of the
             provided type.
            Args:
                entity_type(str): an entity type
                attribute_name(str): the name of the attribute on the parsed intent.
                Defaults to match entity_type.
            Returns:
                self: to continue modifications.
            """
            if not attribute_name:
                attribute_name = entity_type
            self.optional += [(entity_type, attribute_name)]
            return self

        def build(self):
            """
            Constructs an intent from the builder's specifications.
            :return: an Intent instance.
            """
            return Intent(self.name, self.requires,
                          self.at_least_one, self.optional)


class AdaptIntent(IntentBuilder):
    """Wrapper for IntentBuilder setting a blank name.

    Args:
        name (str): Optional name of intent
    """

    def __init__(self, name=''):
        super().__init__(name)

