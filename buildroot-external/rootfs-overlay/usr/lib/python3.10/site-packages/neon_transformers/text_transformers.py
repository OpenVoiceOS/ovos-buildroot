# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2021 Neongecko.com Inc.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions
#    and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions
#    and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#    products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from ovos_plugin_manager.text_transformers import find_utterance_transformer_plugins, load_utterance_transformer_plugin
from ovos_utils.configuration import read_mycroft_config
from ovos_utils.json_helper import merge_dict
from ovos_utils.log import LOG
from ovos_utils.messagebus import get_mycroft_bus
from neon_transformers.tasks import UtteranceTask

class UtteranceTransformer:
    task = UtteranceTask.OTHER

    def __init__(self, name, priority=50, config=None):
        self.name = name
        self.bus = None
        self.priority = priority
        if not config:
            config_core = read_mycroft_config()
            config = config_core.get("utterance_transformers", {}).get(self.name)
        self.config = config or {}

    def bind(self, bus=None):
        """ attach messagebus """
        self.bus = bus or get_mycroft_bus()

    def initialize(self):
        """ perform any initialization actions """
        pass

    def transform(self, utterances, lang="en-us"):
        """ parse utterances
        return modified utterances + metadata to be merged into message context """
        return utterances, {}

    def default_shutdown(self):
        """ perform any shutdown actions """
        pass


class UtteranceTransformersService:

    def __init__(self, bus, config=None):
        self.config_core = config or {}
        self.loaded_modules = {}
        self.has_loaded = False
        self.bus = bus
        self.config = self.config_core.get("utterance_transformers") or {"neon_utterance_translator": {}}
        self.load_plugins()

    def load_plugins(self):
        for plug_name, plug in find_utterance_transformer_plugins().items():
            if plug_name in self.config:
                # if disabled skip it
                if not self.config[plug_name].get("active", True):
                    continue
                try:
                    self.loaded_modules[plug_name] = plug()
                    LOG.info(f"loaded utterance transformer plugin: {plug_name}")
                except Exception as e:
                    LOG.exception(f"Failed to load utterance transformer plugin: {plug_name}")

    @property
    def modules(self):
        return sorted(self.loaded_modules.values(),
                      key=lambda k: k.priority, reverse=True)

    def shutdown(self):
        for module in self.modules:
            try:
                module.shutdown()
            except:
                pass

    def transform(self, utterance, context=None):
        context = context or {}

        for module in self.modules:
            try:
                utterance, data = module.transform(utterance, context)
                LOG.debug(f"{module.name}: {data}")
                context = merge_dict(context, data)
            except:
                pass
        return utterance, context
