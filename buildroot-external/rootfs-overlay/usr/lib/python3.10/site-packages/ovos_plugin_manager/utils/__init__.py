# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Common functions for loading plugins."""
import pkg_resources
from enum import Enum
from ovos_utils.log import LOG
from langcodes import standardize_tag as _normalize_lang


class PluginTypes(str, Enum):
    PHAL = "ovos.plugin.phal"
    ADMIN = "ovos.plugin.phal.admin"
    SKILL = "ovos.plugin.skill"
    VAD = "ovos.plugin.VAD"
    PHONEME = "ovos.plugin.g2p"
    AUDIO = 'mycroft.plugin.audioservice'
    STT = 'mycroft.plugin.stt'
    TTS = 'mycroft.plugin.tts'
    WAKEWORD = 'mycroft.plugin.wake_word'
    TRANSLATE = "neon.plugin.lang.translate"
    LANG_DETECT = "neon.plugin.lang.detect"
    UTTERANCE_TRANSFORMER = "neon.plugin.text"
    METADATA_TRANSFORMER = "neon.plugin.metadata"
    AUDIO_TRANSFORMER = "neon.plugin.audio"
    QUESTION_SOLVER = "neon.plugin.solver"
    COREFERENCE_SOLVER = "intentbox.coreference"
    KEYWORD_EXTRACTION = "intentbox.keywords"
    UTTERANCE_SEGMENTATION = "intentbox.segmentation"
    TOKENIZATION = "intentbox.tokenization"
    POSTAG = "intentbox.postag"


class PluginConfigTypes(str, Enum):
    PHAL = "ovos.plugin.phal.config"
    ADMIN = "ovos.plugin.phal.admin.config"
    SKILL = "ovos.plugin.skill.config"
    VAD = "ovos.plugin.VAD.config"
    PHONEME = "ovos.plugin.g2p.config"
    AUDIO = 'mycroft.plugin.audioservice.config'
    STT = 'mycroft.plugin.stt.config'
    TTS = 'mycroft.plugin.tts.config'
    WAKEWORD = 'mycroft.plugin.wake_word.config'
    TRANSLATE = "neon.plugin.lang.translate.config"
    LANG_DETECT = "neon.plugin.lang.detect.config"
    UTTERANCE_TRANSFORMER = "neon.plugin.text.config"
    METADATA_TRANSFORMER = "neon.plugin.metadata.config"
    AUDIO_TRANSFORMER = "neon.plugin.audio.config"
    QUESTION_SOLVER = "neon.plugin.solver.config"
    COREFERENCE_SOLVER = "intentbox.coreference.config"
    KEYWORD_EXTRACTION = "intentbox.keywords.config"
    UTTERANCE_SEGMENTATION = "intentbox.segmentation.config"
    TOKENIZATION = "intentbox.tokenization.config"
    POSTAG = "intentbox.postag.config"


def find_plugins(plug_type=None):
    """Finds all plugins matching specific entrypoint type.

    Arguments:
        plug_type (str): plugin entrypoint string to retrieve

    Returns:
        dict mapping plugin names to plugin entrypoints
    """
    entrypoints = {}
    if not plug_type:
        plugs = list(PluginTypes)
    elif isinstance(plug_type, str):
        plugs = [plug_type]
    else:
        plugs = plug_type
    for plug in plugs:
        for entry_point in pkg_resources.iter_entry_points(plug):
            try:
                entrypoints[entry_point.name] = entry_point.load()
            except Exception as e:
                LOG.exception(f"Failed to load plugin entry point {entry_point}")
    return entrypoints


def load_plugin(plug_name, plug_type=None):
    """Load a specific plugin from a specific plugin type.

    Arguments:
        plug_type: (str) plugin type name. Ex. "mycroft.plugin.tts".
        plug_name: (str) specific plugin name

    Returns:
        Loaded plugin Object or None if no matching object was found.
    """
    plugins = find_plugins(plug_type)
    if plug_name in plugins:
        return plugins[plug_name]
    LOG.warning('Could not find the plugin {}.{}'.format(
        plug_type or "all plugin types", plug_name))
    return None


def normalize_lang(lang):
    # TODO consider moving to LF or ovos_utils
    try:
        # special handling, the parse sometimes messes this up
        # eg, uk-uk gets normalized to uk-gb
        # this also makes lookup easier as we
        # often get duplicate entries with both variants
        if "-" in lang:
            pieces = lang.split("-")
            if len(pieces) == 2 and pieces[0] == pieces[1]:
                lang = pieces[0]
        lang = _normalize_lang(lang, macro=True)
    except ValueError:
        # this lang code is apparently not valid ?
        pass
    return lang