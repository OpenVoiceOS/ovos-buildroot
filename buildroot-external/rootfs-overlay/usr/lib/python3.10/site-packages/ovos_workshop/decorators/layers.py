import inspect
from functools import wraps
from ovos_utils.log import LOG



def dig_for_skill(max_records: int = 10):
    from ovos_workshop.app import OVOSAbstractApplication
    from ovos_workshop.skills import MycroftSkill
    stack = inspect.stack()[1:]  # First frame will be this function call
    stack = stack if len(stack) <= max_records else stack[:max_records]
    for record in stack:
        args = inspect.getargvalues(record.frame)
        if args.locals.get("self"):
            obj = args.locals["self"]
            if isinstance(obj, MycroftSkill) or \
                    isinstance(obj, OVOSAbstractApplication):
                return obj
        elif args.locals.get("args"):
            for obj in args.locals["args"]:
                if isinstance(obj, MycroftSkill) or \
                        isinstance(obj, OVOSAbstractApplication):
                    return obj
    return None


def enables_layer(layer_name):
    def layer_handler(func):
        @wraps(func)
        def call_function(*args, **kwargs):
            skill = dig_for_skill()
            skill.intent_layers = skill.intent_layers or \
                                  IntentLayers().bind(skill)
            func(*args, **kwargs)
            skill.intent_layers.activate_layer(layer_name)

        return call_function

    return layer_handler


def disables_layer(layer_name):
    def layer_handler(func):
        @wraps(func)
        def call_function(*args, **kwargs):
            skill = dig_for_skill()
            skill.intent_layers = skill.intent_layers or \
                                  IntentLayers().bind(skill)
            func(*args, **kwargs)
            skill.intent_layers.deactivate_layer(layer_name)

        return call_function

    return layer_handler


def replaces_layer(layer_name, intent_list):
    def layer_handler(func):
        @wraps(func)
        def call_function(*args, **kwargs):
            skill = dig_for_skill()
            skill.intent_layers = skill.intent_layers or \
                                  IntentLayers().bind(skill)
            func(*args, **kwargs)
            skill.intent_layers.replace_layer(layer_name, intent_list)

        return call_function

    return layer_handler


def removes_layer(layer_name, intent_list):
    def layer_handler(func):
        @wraps(func)
        def call_function(*args, **kwargs):
            skill = dig_for_skill()
            skill.intent_layers = skill.intent_layers or \
                                  IntentLayers().bind(skill)
            func(*args, **kwargs)
            skill.intent_layers.replace_layer(layer_name, intent_list)

        return call_function

    return layer_handler


def resets_layers():
    def layer_handler(func):
        @wraps(func)
        def call_function(*args, **kwargs):
            skill = dig_for_skill()
            skill.intent_layers = skill.intent_layers or \
                                  IntentLayers().bind(skill)
            func(*args, **kwargs)
            skill.intent_layers.disable()

        return call_function

    return layer_handler


def layer_intent(intent_parser, layer_name):
    """Decorator for adding a method as an intent handler belonging to an
    intent layer."""

    def real_decorator(func):
        # Store the intent_parser inside the function
        # This will be used later to call register_intent
        if not hasattr(func, 'intents'):
            func.intents = []
        if not hasattr(func, 'intent_layers'):
            func.intent_layers = {}

        func.intents.append(intent_parser)
        if layer_name not in func.intent_layers:
            func.intent_layers[layer_name] = []

        # get intent_name
        if hasattr(intent_parser, "build"):
            intent = intent_parser.build()
            intent_name = intent.name or func.__name__
        elif hasattr(intent_parser, "name"):
            intent_name = intent_parser.name
        else:
            intent_name = intent_parser
    
        func.intent_layers[layer_name].append(intent_name)
        return func

    return real_decorator


class IntentLayers:
    def __init__(self):
        self._skill = None
        self._layers = {}
        self._active_layers = []

    def bind(self, skill):
        if skill:
            self._skill = skill
        return self

    @property
    def skill(self):
        return self._skill

    @property
    def bus(self):
        return self._skill.bus if self._skill else None

    @property
    def skill_id(self):
        return self._skill.skill_id if self._skill else "IntentLayers"

    @property
    def active_layers(self):
        return self._active_layers

    def disable(self):
        LOG.info("Disabling layers")
        # disable all layers
        for layer_name, intents in self._layers.items():
            self.deactivate_layer(layer_name)

    def update_layer(self, layer_name, intent_list=None):
        if not layer_name.startswith(f"{self.skill_id}:"):
            layer_name = f"{self.skill_id}:{layer_name}"
        intent_list = intent_list or []
        if layer_name not in self._layers:
            self._layers[layer_name] = []
        self._layers[layer_name] += intent_list or []
        LOG.info(f"Adding {intent_list} to {layer_name}")

    def activate_layer(self, layer_name):
        if not layer_name.startswith(f"{self.skill_id}:"):
            layer_name = f"{self.skill_id}:{layer_name}"
        if layer_name in self._layers:
            LOG.info("activating layer named: " + layer_name)
            if layer_name not in self._active_layers:
                self._active_layers.append(layer_name)
            for intent in self._layers[layer_name]:
                self.skill.enable_intent(intent)
        else:
            LOG.debug("no layer named: " + layer_name)

    def deactivate_layer(self, layer_name):
        if not layer_name.startswith(f"{self.skill_id}:"):
            layer_name = f"{self.skill_id}:{layer_name}"
        if layer_name in self._layers:
            LOG.info("deactivating layer named: " + layer_name)
            if layer_name in self._active_layers:
                self._active_layers.remove(layer_name)
            for intent in self._layers[layer_name]:
                self.skill.disable_intent(intent)
        else:
            LOG.debug("no layer named: " + layer_name)

    def remove_layer(self, layer_name):
        if not layer_name.startswith(f"{self.skill_id}:"):
            layer_name = f"{self.skill_id}:{layer_name}"
        if layer_name in self._layers:
            self.deactivate_layer(layer_name)
            LOG.info("removing layer named: " + layer_name)
            self._layers.pop(layer_name)
        else:
            LOG.debug("no layer named: " + layer_name)

    def replace_layer(self, layer_name, intent_list=None):
        if not layer_name.startswith(f"{self.skill_id}:"):
            layer_name = f"{self.skill_id}:{layer_name}"
        if layer_name in self._layers:
            LOG.info("replacing layer named: " + layer_name)
            self._layers[layer_name] = intent_list or []
        else:
            self.update_layer(layer_name, intent_list)

    def is_active(self, layer_name):
        if not layer_name.startswith(f"{self.skill_id}:"):
            layer_name = f"{self.skill_id}:{layer_name}"
        return layer_name in self.active_layers

