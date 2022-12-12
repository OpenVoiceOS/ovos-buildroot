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
from enum import Enum
from time import sleep

from adapt.intent import IntentBuilder
from mycroft.messagebus.message import Message
from mycroft.skills.core import intent_handler
from ovos_backend_client.backends import BackendType, get_backend_type
from ovos_backend_client.backends.selene import SELENE_API_URL, SELENE_PRECISE_URL
from ovos_backend_client.pairing import PairingManager, is_paired, check_remote_pairing
from ovos_config.config import update_mycroft_config
from ovos_plugin_manager.utils.ui import PluginUIHelper, PluginTypes
from ovos_utils.device_input import can_use_touch_mouse
from ovos_utils.gui import is_gui_running
from ovos_utils.log import LOG
from ovos_utils.network_utils import is_connected
from ovos_workshop.decorators import killable_event
from ovos_workshop.skills import OVOSSkill


class SetupState(str, Enum):
    FIRST_BOOT = "first"
    LOADING = "loading"
    INACTIVE = "inactive"
    SELECTING_WIFI = "wifi"
    WELCOME = "welcome"
    SELECTING_LANGUAGE = "language"
    SELECTING_BACKEND = "backend"
    SELECTING_STT = "stt"
    SELECTING_TTS = "tts"
    PAIRING = "pairing"
    FINISHED = "finished"


class PairingMode(str, Enum):
    VOICE = "voice"  # voice only
    GUI = "gui"  # gui - click buttons


class SetupManager:
    """ helper class to perform setup actions"""

    def __init__(self, bus):
        self.bus = bus
        # simplified voice only route
        self._offline_male = {
            "module": "ovos-tts-plugin-mimic",
            "ovos-tts-plugin-mimic": {"voice": "ap"}
        }
        self._online_male = {
            "module": "ovos-tts-plugin-mimic2",
            "ovos-tts-plugin-mimic2": {"voice": "kusal"}
        }
        self._offline_female = {
            "module": "ovos-tts-plugin-pico",
            "ovos-tts-plugin-pico": {}
        }
        self._online_female = {
            "module": "neon-tts-plugin-larynx-server",
            "neon-tts-plugin-larynx-server": {
                "voice": "mary_ann",
                "vocoder": "hifi_gan/vctk_small"
            }
        }
        self._online_stt = {
            "module": "ovos-stt-plugin-server",
            "fallback_module": "ovos-stt-plugin-vosk",
            # vosk model path not set, small model for lang auto downloaded to XDG directory
            # en-us already bundled in OVOS image
            "ovos-stt-plugin-vosk": {},
            "ovos-stt-plugin-server": {
                "url": "https://stt.openvoiceos.com/stt"
            }
        }
        self._offline_stt = {
            "module": "ovos-stt-plugin-vosk-streaming",
            "fallback_module": "",  # disable fallback STT to avoid loading vosk twice
            # vosk model path not set, small model for lang auto downloaded to XDG directory
            # en-us already bundled in OVOS image
            "ovos-stt-plugin-vosk": {},
            "ovos-stt-plugin-vosk-streaming": {}
        }

    @property
    def offline_stt_module(self):
        return self._offline_stt.get("module") or "ovos-stt-plugin-vosk"

    @property
    def online_stt_module(self):
        return self._online_stt.get("module") or "ovos-stt-plugin-server"

    @property
    def online_male_tts_module(self):
        return self._online_male.get("module") or "ovos-tts-plugin-mimic2"

    @property
    def online_female_tts_module(self):
        return self._online_female.get("module") or "neon-tts-plugin-larynx-server"

    @property
    def offline_male_tts_module(self):
        return self._offline_male.get("module") or "ovos-tts-plugin-mimic"

    @property
    def offline_female_tts_module(self):
        return self._offline_female.get("module") or "ovos-tts-plugin-pico"

    # options configuration
    def set_offline_stt_opt(self, module, config, fallback_module="", fallback_config=None):
        self._offline_stt = {"module": module, "fallback_module": fallback_module, module: config}
        if fallback_module:
            self._offline_stt[fallback_module] = fallback_config or {}

    def set_online_stt_opt(self, module, config, fallback_module="", fallback_config=None):
        self._online_stt = {"module": module, "fallback_module": fallback_module, module: config}
        if fallback_module:
            self._online_stt[fallback_module] = fallback_config or {}

    def set_offline_male_opt(self, module, config):
        self._offline_male = {"module": module, module: config}

    def set_offline_female_opt(self, module, config):
        self._offline_female = {"module": module, module: config}

    def set_online_male_opt(self, module, config):
        self._online_male = {"module": module, module: config}

    def set_online_female_opt(self, module, config):
        self._online_female = {"module": module, module: config}

    # config handling
    def change_tts(self, opt):
        tts_module = opt["engine"]
        if "plugin_type" not in opt:
            opt["plugin_type"] = PluginTypes.TTS
        cfg = PluginUIHelper.option2config(opt, PluginTypes.TTS)
        # plugins report an extra "meta" key for UI consumption, filter it
        if "meta" in cfg:
            cfg.pop("meta")
        tts_cfg = {"module": tts_module,
                   tts_module: cfg}
        update_mycroft_config({"tts": tts_cfg}, bus=self.bus)

    def change_stt(self, opt):
        stt_module = opt["engine"]
        if "plugin_type" not in opt:
            opt["plugin_type"] = PluginTypes.STT
        cfg = PluginUIHelper.option2config(opt, PluginTypes.STT)
        # plugins report an extra "meta" key for UI consumption, filter it
        if "meta" in cfg:
            cfg.pop("meta")
        stt_cfg = {"module": stt_module, stt_module: cfg}
        update_mycroft_config({"stt": stt_cfg}, bus=self.bus)

    def change_to_offline_male(self):
        update_mycroft_config({"tts": self._offline_male},
                              bus=self.bus)

    def change_to_online_male(self):
        update_mycroft_config({"tts": self._online_male},
                              bus=self.bus)

    def change_to_online_female(self):
        update_mycroft_config({"tts": self._online_female},
                              bus=self.bus)

    def change_to_offline_female(self):
        update_mycroft_config({"tts": self._offline_female},
                              bus=self.bus)

    def change_to_online_stt(self):
        update_mycroft_config({"stt": self._online_stt},
                              bus=self.bus)

    def change_to_offline_stt(self):
        update_mycroft_config({"stt": self._offline_stt},
                              bus=self.bus)

    def change_to_selene(self):
        config = {
            "stt": {"module": "ovos-stt-plugin-selene"},
            "server": {
                "url": SELENE_API_URL,
                "version": "v1",
                "backend_type": BackendType.SELENE.value
            },
            "listener": {
                "wake_word_upload": {
                    "url": SELENE_PRECISE_URL
                }
            }
        }
        update_mycroft_config(config, bus=self.bus)

    def change_to_local_backend(self, url="http://0.0.0.0:6712"):
        config = {
            "stt": {"module": "ovos-stt-plugin-selene"},
            "server": {
                "url": url,
                "version": "v1",
                "backend_type": BackendType.PERSONAL.value
            },
            "listener": {
                "wake_word_upload": {
                    "url": f"{url}/precise/upload"
                }
            }
        }
        update_mycroft_config(config, bus=self.bus)

    def change_to_no_backend(self):
        config = {
            "server": {
                "backend_type": BackendType.OFFLINE.value
            }
        }
        update_mycroft_config(config, bus=self.bus)


class PairingSkill(OVOSSkill):

    def __init__(self):
        super(PairingSkill, self).__init__("PairingSkill")
        self.reload_skill = False
        self.translations = dict()
        self.setup = None
        self.pairing = None
        self.mycroft_ready = False
        self._state = SetupState.LOADING
        self.selected_language = None

    @property
    def pairing_mode(self):
        if not is_gui_running() or not can_use_touch_mouse():
            return PairingMode.VOICE
        else:
            return PairingMode.GUI

    # startup
    def initialize(self):
        self.pairing = PairingManager(self.bus,
                                      code_callback=self.on_pairing_code,
                                      success_callback=self.on_pairing_success,
                                      end_callback=self.on_pairing_end,
                                      start_callback=self.on_pairing_start,
                                      restart_callback=self.handle_pairing,
                                      error_callback=self.on_pairing_error)
        self._init_setup_options()

        # set default language
        self.selected_language = self.lang.split("-")[0].lower()
        if self.selected_language not in [l["code"] for l in self.settings["langs"]]:
            LOG.warning(f"Default language is not available in {self.skill_id}")
            self.selected_language = "en"

        self.add_event("mycroft.not.paired", self.not_paired)
        self.add_event("ovos.setup.state.get", self.handle_get_setup_state)

        # events for GUI interaction
        self.gui.register_handler("mycroft.device.set.backend", self.handle_backend_selected_event)
        self.gui.register_handler("mycroft.device.confirm.backend", self.handle_backend_confirmation_event)
        self.gui.register_handler("mycroft.device.local.setup.host.address", self.handle_personal_backend_url)
        self.gui.register_handler("mycroft.return.select.backend", self.handle_return_event)
        self.gui.register_handler("mycroft.device.confirm.stt", self.handle_stt_selected)
        self.gui.register_handler("mycroft.device.confirm.tts", self.handle_tts_selected)
        self.gui.register_handler("mycroft.device.confirm.language", self.handle_language_selected)
        self.gui.register_handler("mycroft.return.select.language", self.handle_language_back_event)

        # translations
        self.translations["code"] = self.translate_namedvalues("code.spelling")
        self.translations["backend"] = self.translate_namedvalues("options.backend")
        self.translations["stt"] = self.translate_namedvalues("options.stt")
        self.translations["tts"] = self.translate_namedvalues("options.tts")

        self._init_state()

    def _init_setup_options(self):
        # distros/images can customize setup by placing a json file in skill settings XDG location
        self.setup = SetupManager(self.bus)

        # configure setup steps based on skill settings, this allows distros to skip some aspects of setup
        if "enable_language_selection" not in self.settings:
            self.settings["enable_language_selection"] = False
        if "enable_backend_selection" not in self.settings:
            self.settings["enable_backend_selection"] = True
        if "enable_stt_selection" not in self.settings:
            self.settings["enable_stt_selection"] = True
        if "enable_tts_selection" not in self.settings:
            self.settings["enable_tts_selection"] = True

        if "preferred_tts_engine" not in self.settings:
            self.settings["preferred_tts_engine"] = ""
        if "preferred_stt_engine" not in self.settings:
            self.settings["preferred_stt_engine"] = ""

        # limit selectable plugins
        if "tts_blacklist" not in self.settings:
            self.settings["tts_blacklist"] = ["ovos-tts-plugin-SAM",
                                              "ovos-tts-plugin-beepspeak",
                                              "ovos_tts_plugin_espeakng"]
        if "stt_blacklist" not in self.settings:
            self.settings["stt_blacklist"] = ["ovos-stt-plugin-pocketsphinx"]

        # configure selectable languages
        if "langs" not in self.settings:
            # Name: display name to display in UI
            # Code: Used by ovos shell locale, get tts and stt engines
            # System Code: Used by system as full code is required
            self.settings["langs"] = [
                {"name": "English", "code": "en", "system_code": "en_US"},
                {"name": "Italian", "code": "it", "system_code": "it_IT"},
                {"name": "French", "code": "fr", "system_code": "fr_FR"},
                {"name": "Spanish", "code": "es", "system_code": "es_ES"},
                {"name": "Portuguese", "code": "pt", "system_code": "pt_PT"},
                {"name": "German", "code": "de", "system_code": "de_DE"},
                {"name": "Dutch", "code": "nl", "system_code": "nl_NL"}
            ]

        # read default plugins for simplified voice route from settings
        # TODO - validate that these are in fact installed
        # TODO - parse default value from OPM sorted list,
        #  should ensure "best installed" plugin is used
        if self.settings.get("offline_stt"):
            engine = self.settings.get("offline_stt")
            fallback = self.settings.get("offline_fallback_stt")
            cfg = self.settings.get("offline_stt_cfg")
            fallback_cfg = self.settings.get("offline_fallback_stt_cfg")
            self.setup.set_offline_stt_opt(engine, cfg, fallback, fallback_cfg)
        if self.settings.get("online_stt"):
            engine = self.settings.get("online_stt")
            fallback = self.settings.get("online_fallback_stt")
            cfg = self.settings.get("online_stt_cfg")
            fallback_cfg = self.settings.get("online_fallback_stt_cfg")
            self.setup.set_online_stt_opt(engine, cfg, fallback, fallback_cfg)
        if self.settings.get("online_male"):
            engine = self.settings.get("online_male")
            cfg = self.settings.get("online_male_cfg")
            self.setup.set_online_male_opt(engine, cfg)
        if self.settings.get("online_female"):
            engine = self.settings.get("online_female")
            cfg = self.settings.get("online_female_cfg")
            self.setup.set_online_female_opt(engine, cfg)
        if self.settings.get("offline_male"):
            engine = self.settings.get("offline_male")
            cfg = self.settings.get("offline_male_cfg")
            self.setup.set_offline_male_opt(engine, cfg)
        if self.settings.get("offline_female"):
            engine = self.settings.get("offline_female")
            cfg = self.settings.get("offline_female_cfg")
            self.setup.set_offline_female_opt(engine, cfg)

    def _init_state(self):
        self.first_setup = self.settings.get("first_setup", True)
        # uncomment this line for debugging
        # will always trigger setup on boot
        # self.first_setup = True

        if not is_connected():
            self.state = SetupState.SELECTING_WIFI
            # trigger pairing after wifi
            self.bus.once("ovos.wifi.setup.completed",
                          self.handle_wifi_finish)
            self.bus.once("ovos.phal.wifi.plugin.skip.setup",
                          self.handle_wifi_skip)
        elif self.first_setup:
            self.state = SetupState.FIRST_BOOT
            self.make_active()  # to enable converse
            self.bus.emit(Message("mycroft.not.paired"))
        elif not is_paired():
            # trigger pairing
            self.state = SetupState.SELECTING_BACKEND
            self.bus.emit(Message("mycroft.not.paired"))
        else:
            self.handle_display_manager("LoadingSkills")
            self.pairing.api.update_version()
            self.end_setup(True)

    def _translate(self, section: str, key: str = None):
        if key is None:
            return self.translations.get(section, {})
        return self.translations.get(section, {}).get(key, "")

    @property
    def backend_type(self):
        return get_backend_type(self.config_core)

    @property
    def selected_backend(self):
        return self.settings.get("selected_backend")

    @selected_backend.setter
    def selected_backend(self, value):
        self.settings["selected_backend"] = value
        self.settings.store()

    @property
    def selected_stt(self):
        return self.settings.get("selected_stt")

    @selected_stt.setter
    def selected_stt(self, value):
        self.settings["selected_stt"] = value
        self.settings.store()

    @property
    def selected_tts(self):
        return self.settings.get("selected_tts")

    @selected_tts.setter
    def selected_tts(self, value):
        self.settings["selected_tts"] = value
        self.settings.store()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if value != self._state:
            self._state = value
            self.bus.emit(Message("ovos.setup.state", {"state": self._state}))

    def handle_get_setup_state(self, message):
        self.bus.emit(message.reply("ovos.setup.state",
                                    {"state": self.state}))

    def handle_wifi_finish(self, message):
        self.handle_display_manager("LoadingScreen")
        if not is_paired() or self.first_setup:
            self.state = SetupState.SELECTING_BACKEND
            self.bus.emit(message.forward("mycroft.not.paired"))
        else:
            self.end_setup()

    def handle_wifi_skip(self, message):
        LOG.info("Offline mode selected, setup will resume on restart")
        self.handle_display_manager("OfflineMode")
        self.end_setup(success=False)

    def handle_intent_aborted(self):
        LOG.info("killing all dialogs")

    def not_paired(self, message):
        self.make_active()  # to enable converse
        # If the device isn't paired catch mycroft.ready to release gui
        self.bus.once("mycroft.ready", self.handle_mycroft_ready)
        if not message.data.get('quiet', True):
            self.speak_dialog("pairing.not.paired", wait=True)
        self.handle_pairing()

    def handle_mycroft_ready(self, message):
        """Catch info that skills are loaded and ready."""
        self.mycroft_ready = True
        # clear gui, either the pairing page or the initial loading page
        self.gui.remove_page("ProcessLoader.qml")
        self.bus.emit(Message("mycroft.gui.screen.close",
                              {"skill_id": self.skill_id}))
        self.state = SetupState.INACTIVE

    # voice events
    def converse(self, message):
        if self.pairing_mode != PairingMode.GUI:
            if self.state != SetupState.INACTIVE and \
                    self.state != SetupState.FINISHED:
                # capture all utterances until paired
                # prompts from this skill are handled with get_response
                return True
            return False

    @intent_handler(IntentBuilder("PairingIntent")
                    .require("pairing").require("device"))
    def handle_pairing(self, message=None):
        self.state = SetupState.SELECTING_BACKEND
        if message:  # intent
            if self.backend_type in [BackendType.SELENE, BackendType.PERSONAL]:
                if check_remote_pairing(ignore_errors=True):
                    # Already paired!
                    self.show_pairing_success()
                    self.speak_dialog("pairing.already.paired", wait=True)
                    self.end_setup(success=True)
                    return

        # trigger setup workflow
        self.handle_welcome_screen()

    # pairing callbacks
    def on_pairing_start(self):
        self.state = SetupState.PAIRING
        self.show_pairing_start()

        if self.backend_type == BackendType.SELENE:
            self.speak_dialog("pairing.intro", wait=True)

    def on_pairing_code(self, code):
        data = {"code": '. '.join(map(self._translate("code").get, code)) + '.'}
        self.show_pairing(code)
        self.speak_dialog("pairing.code", data, wait=True)

    def on_pairing_success(self):
        self.show_pairing_success()

        if self.mycroft_ready:
            # Tell user they are now paired
            self.speak_dialog("pairing.paired", wait=True)

        # allow gui page to linger around a bit
        sleep(5)
        self.handle_display_manager("LoadingSkills")
        self.pairing.api.update_version()
        self.end_setup(success=True)

    def on_pairing_error(self, quiet):
        self.show_pairing_fail()
        if not quiet:
            self.speak_dialog("error.unexpected.restarting", wait=True)
        self.end_setup(success=False)

    def on_pairing_end(self, error_dialog):
        if error_dialog:
            self.speak_dialog(error_dialog, wait=True)
            self.end_setup(success=False)
        else:
            self.end_setup(success=True)

    # Pairing GUI events
    ### Language Selection & Welcome Screen
    def handle_welcome_screen(self):
        self.state = SetupState.WELCOME
        self.handle_display_manager("Welcome")
        sleep(0.3)  # Wait for display to show the screen before speaking
        self.speak_dialog("welcome.screen", wait=True)
        sleep(0.3)  # Wait for display a bit before showing the next screen
        if self.pairing_mode != PairingMode.GUI:
            self.handle_backend_menu()
        else:
            lang_support_enabled = self.settings.get("enable_language_selection", False)
            if not lang_support_enabled:
                self.gui["language_selection_enabled"] = False
                self.handle_backend_menu()
            else:
                self.gui["language_selection_enabled"] = True
                self.handle_language_menu()

    def handle_language_menu(self):
        self.state = SetupState.SELECTING_LANGUAGE
        supported_languages = self.settings["langs"]
        self.gui["supportedLanguagesModel"] = supported_languages
        self.handle_display_manager("LanguageMenu")
        self.speak_dialog("language.menu", wait=True)

    def handle_language_selected(self, message):
        self.selected_language = message.data["code"]
        system_code = message.data["system_code"]
        self.bus.emit(Message("system.configure.language",
                              {"code": self.selected_language,
                               "language_code": system_code}))
        self.handle_backend_menu()

    def handle_language_back_event(self, message):
        self.handle_language_menu()

    #### Backend selection menu
    @killable_event(msg="pairing.backend.menu.stop")
    def handle_backend_menu(self):
        if not self.settings["enable_backend_selection"]:
            if not is_paired():
                self.handle_no_backend_selected(None)
            else:
                self.handle_stt_menu()
            return

        self.state = SetupState.SELECTING_BACKEND
        self.send_stop_signal("pairing.confirmation.stop")
        self.handle_display_manager("BackendSelect")
        self.speak_dialog("backend.intro", wait=True)
        if self.pairing_mode != PairingMode.VOICE:
            self.speak_dialog("options.select.gui", wait=True)

        if self.pairing_mode != PairingMode.GUI:
            self.speak_dialog("backend.options.intro", wait=True)
            self.speak_dialog("backend.selene", wait=True)
            self._backend_menu_voice()

    def _backend_menu_voice(self, wait=0):
        sleep(int(wait))
        answer = self.get_response("backend.prompt", num_retries=0)
        if answer:
            LOG.debug("Backend select answer (voice): " + answer)
            if self.voc_match(answer, "offline"):
                self.bus.emit(Message(f"{self.skill_id}.mycroft.device.set.backend",
                                      {"backend": BackendType.OFFLINE.value}))
                return
            elif self.voc_match(answer, "personal"):
                self.bus.emit(Message(f"{self.skill_id}.mycroft.device.set.backend",
                                      {"backend": BackendType.PERSONAL.value}))
                return
            elif self.voc_match(answer, "selene"):
                self.bus.emit(Message(f"{self.skill_id}.mycroft.device.set.backend",
                                      {"backend": BackendType.SELENE.value}))
                return
            else:
                self.speak_dialog("backend.not.understood", wait=True)

        sleep(1)  # time for abort to kick in
        # (answer will be None and return before this is killed)
        self._backend_menu_voice(wait=3)

    def handle_backend_selected_event(self, message):
        self.send_stop_signal("pairing.backend.menu.stop")
        self.handle_backend_confirmation(message.data["backend"])

    def handle_return_event(self, message):
        self.send_stop_signal("pairing.confirmation.stop")
        page = message.data.get("page", "")
        self.handle_backend_menu()

    ### Backend confirmation
    @killable_event(msg="pairing.confirmation.stop",
                    callback=handle_intent_aborted)
    def handle_backend_confirmation(self, selection):
        LOG.debug("Backend selected: " + selection)
        if selection not in (BackendType.SELENE,
                             BackendType.OFFLINE,
                             BackendType.PERSONAL):
            raise ValueError(f"Invalid selection: {selection}")
        self.speak_dialog(f"backend.confirm.intro.{selection}", wait=True)

        if self.pairing_mode != PairingMode.VOICE:
            self.handle_display_manager(f"Backend{selection.title()}")
            self.speak_dialog("backend.confirm.gui",
                              {'backend': self._translate("backend", selection)},
                              wait=True)
        if self.pairing_mode != PairingMode.GUI:
            self._backend_confirmation_voice(selection)

    def _backend_confirmation_voice(self, selection):
        self.speak_dialog(f"backend.selected.{selection}", wait=True)
        ans = self.ask_yesno("backend.confirm",
                             {"backend": self._translate("backend", selection)})
        LOG.debug("Backend confirmation answer (voice): " + ans)
        if ans == "yes":
            self.bus.emit(Message(f"{self.skill_id}.mycroft.device.confirm.backend",
                                  {"backend": selection}))
        elif ans == "no":
            self._backend_menu_voice(wait=3)
        else:
            sleep(3)  # time for abort to kick in
            # (answer will be None and return before this is killed)
            self._backend_confirmation_voice(selection)

    def handle_backend_confirmation_event(self, message):
        self.send_stop_signal("pairing.confirmation.stop")
        if message.data["backend"] == BackendType.PERSONAL:
            self.handle_personal_backend_selected(message)
        elif message.data["backend"] == BackendType.SELENE:
            self.handle_selene_selected(message)
        else:
            self.handle_no_backend_selected(message)

    def handle_selene_selected(self, message):
        self.pairing.pairing_url = self.settings["pairing_url"] = "home.mycroft.ai"  # scroll in mk1 faceplate
        # this will make a new DeviceApi object internally pointing to right url
        self.pairing.set_api_url(SELENE_API_URL, backend_type=BackendType.SELENE)
        # selene selected
        self.setup.change_to_selene()
        # continue to normal pairing process
        self.state = SetupState.PAIRING
        self.pairing.kickoff_pairing()

    def handle_personal_backend_selected(self, message):
        self.handle_display_manager("BackendPersonalHost")
        self.speak_dialog("backend.personal.url.prompt", wait=True)

    def handle_personal_backend_url(self, message):
        host = message.data["host_address"]
        self.pairing.pairing_url = self.settings["pairing_url"] = host
        # this will make a new DeviceApi object internally pointing to right url
        self.pairing.set_api_url(host, backend_type=BackendType.PERSONAL)
        self.setup.change_to_local_backend(host)
        # continue to normal pairing process
        self.state = SetupState.PAIRING
        # dont trigger loop
        self.pairing.activator_cancelled = True
        # auto-pair
        self.pairing.kickoff_pairing()
        self.pairing.check_for_activate()
        self.pairing.activator_cancelled = False

    def handle_no_backend_selected(self, message):
        self.pairing.pairing_url = self.settings["pairing_url"] = ""
        # this will make a new DeviceApi object internally pointing to right url
        self.pairing.set_api_url("127.0.0.1", backend_type=BackendType.OFFLINE)
        self.pairing.data = None
        self.setup.change_to_no_backend()
        # auto pair
        self.pairing.api.activate(self.pairing.uuid, "123ABC")
        # continue to STT
        self.handle_stt_menu()

    ### STT selection
    @killable_event(msg="pairing.stt.menu.stop",
                    callback=handle_intent_aborted)
    def handle_stt_menu(self):
        if not self.settings["enable_stt_selection"]:
            if self.settings["enable_tts_selection"]:
                self.handle_tts_menu()
            else:
                self.end_setup(success=True)
            return

        self.state = SetupState.SELECTING_STT
        supported_stt_engines = PluginUIHelper.get_config_options(self.selected_language, PluginTypes.STT,
                                                                  self.settings["stt_blacklist"],
                                                                  self.settings["preferred_stt_engine"])
        self.log.info("Supported STT engines: " + str(supported_stt_engines))
        self.gui["stt_engines"] = supported_stt_engines
        self.handle_display_manager("STTListMenu")
        self.send_stop_signal("pairing.confirmation.stop")
        self.speak_dialog("stt.intro", wait=True)
        if self.pairing_mode != PairingMode.VOICE:
            self.speak_dialog("options.select.gui", wait=True)
        if self.pairing_mode != PairingMode.GUI:
            self._stt_menu_voice()

    def _stt_menu_voice(self):
        options = self._translate("stt").values()
        ans = self.ask_selection(options, "selection.ask.intro", min_conf=0.35)
        LOG.debug("STT select answer (voice): " + ans)
        if ans and self.ask_yesno("stt.confirm", {"stt": ans}) == "yes":
            engine = self.setup.online_stt_module \
                if ans == self._translate("sst", "online") else self.setup.offline_stt_module
            self.bus.emit(Message(f"{self.skill_id}.mycroft.device.confirm.stt",
                                  {"engine": engine}))
        else:
            self.speak_dialog("choice.failed", wait=True)
            self._stt_menu_voice()

    def handle_stt_selected(self, message):
        self.selected_stt = message.data["engine"]
        if self.pairing_mode == PairingMode.VOICE:
            if self.selected_stt == self.setup.online_stt_module:
                self.setup.change_to_online_stt()
            else:
                self.setup.change_to_offline_stt()
        else:
            self.setup.change_stt(message.data)
        self.send_stop_signal("pairing.stt.menu.stop")
        self.handle_tts_menu()

    ### TTS selection
    @killable_event(msg="pairing.tts.menu.stop",
                    callback=handle_intent_aborted)
    def handle_tts_menu(self):
        if not self.settings["enable_tts_selection"]:
            self.end_setup(success=True)
            return

        self.state = SetupState.SELECTING_TTS

        single = self.settings.get("single_tts_list")
        opts = PluginUIHelper.get_config_options(self.selected_language, PluginTypes.TTS,
                                                 self.settings["tts_blacklist"],
                                                 self.settings["preferred_tts_engine"],
                                                 max_opts=50)
        plug_opts = PluginUIHelper.get_plugin_options(self.selected_language, PluginTypes.TTS)
        if len(plug_opts) == 1:
            single = True  # only 1 plugin installed, skip plugin selection and show voices directly

        if single is None:
            # auto detect best display option
            if len(opts) >= 25:
                single = False
            else:
                single = True

        self.gui["tts_engines"] = opts if single else plug_opts

        if single:
            self.handle_display_manager("TTSListMenuSingle")
        else:
            self.handle_display_manager("TTSListMenuNested")

        self.send_stop_signal("pairing.stt.menu.stop")
        self.speak_dialog("tts.intro", wait=True)
        if self.pairing_mode != PairingMode.VOICE:
            self.speak_dialog("options.select.gui", wait=True)
        if self.pairing_mode != PairingMode.GUI:
            self._tts_menu_voice()

    def _tts_menu_voice(self):
        options = self._translate("tts").values()
        ans = self.ask_selection(options, "selection.ask.intro", min_conf=0.35)
        if ans and self.ask_yesno("tts.confirm", {"tts": ans}) == "yes":
            tts = self.setup.online_male_tts_module
            if ans == self._translate("tts", "offline male"):
                tts = self.setup.offline_male_tts_module
            elif ans == self._translate("tts", "online female"):
                tts = self.setup.online_female_tts_module
            elif ans == self._translate("tts", "offline female"):
                tts = self.setup.offline_female_tts_module
            self.bus.emit(Message(f'{self.skill_id}.mycroft.device.confirm.tts',
                                  {"engine": tts}))
        else:
            self.speak_dialog("choice.failed", wait=True)
            self._tts_menu_voice()

    def handle_tts_selected(self, message):
        self.selected_tts = message.data["engine"]
        if self.pairing_mode == PairingMode.VOICE:
            if self.selected_tts == self.setup.offline_male_tts_module:
                self.setup.change_to_offline_male()
            elif self.selected_tts == self.setup.online_male_tts_module:
                self.setup.change_to_online_male()
            elif self.selected_tts == self.setup.offline_female_tts_module:
                self.setup.change_to_offline_female()
            elif self.selected_tts == self.setup.online_female_tts_module:
                self.setup.change_to_online_female()
        else:
            self.setup.change_tts(message.data)

        self.send_stop_signal("pairing.tts.menu.stop")
        self.end_setup(success=True)

    def end_setup(self, success=False):
        if self.state != SetupState.INACTIVE:
            self.handle_display_manager("LoadingSkills")
            if success:  # dont restart setup on next boot
                self.settings["first_setup"] = False
            self.state = SetupState.FINISHED
            self.bus.emit(Message("ovos.setup.finished"))  # tell skill manager to stop waiting for pairing step

    # GUI
    def handle_display_manager(self, state):
        self.gui["state"] = state
        self.gui.show_page(
            "ProcessLoader.qml",
            override_idle=True,
            override_animations=True)

    def show_pairing_start(self):
        self.handle_display_manager("PairingStart")
        # self.gui.show_page("pairing_start.qml", override_idle=True,
        # override_animations=True)

    def show_pairing(self, code):
        # self.gui.remove_page("pairing_start.qml")
        self.gui["backendurl"] = self.settings.get("pairing_url") or "home.mycroft.ai"
        self.gui["code"] = code
        self.handle_display_manager("Pairing")
        # self.gui.show_page("pairing.qml", override_idle=True,
        # override_animations=True)

    def show_pairing_success(self):
        # self.gui.remove_page("pairing.qml")
        self.gui["status"] = "Success"
        self.gui["label"] = "Device Paired"
        self.gui["bgColor"] = "#40DBB0"
        # self.gui.show_page("status.qml", override_idle=True,
        # override_animations=True)
        self.handle_display_manager("Status")

    def show_pairing_fail(self):
        self.gui.release()
        self.gui["status"] = "Failed"
        self.gui["label"] = "Pairing Failed"
        self.gui["bgColor"] = "#FF0000"
        self.handle_display_manager("Status")
        sleep(5)

    def shutdown(self):
        self.pairing.shutdown()


def create_skill():
    return PairingSkill()
