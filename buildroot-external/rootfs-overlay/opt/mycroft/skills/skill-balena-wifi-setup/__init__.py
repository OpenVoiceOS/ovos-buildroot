from mycroft import MycroftSkill, intent_handler
from mycroft.util import create_daemon, connected
from mycroft.configuration import LocalConf, USER_CONFIG
import subprocess
import pexpect
from time import sleep


class WifiConnect(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.monitoring = False
        self.in_setup = False
        self.wifi_process = None
        self.debug = False  # dev setting, VERY VERBOSE DIALOGS
        # TODO skill settings
        self.ssid = "OVOS"
        self.pswd = None
        self.grace_period = 45
        self.time_between_checks = 30  # seconds
        self.wifi_command = "sudo /usr/local/sbin/wifi-connect --portal-ssid {ssid}"
        if self.pswd:
            self.wifi_command += " --portal-passphrase {pswd}"
        if "color" not in self.settings:
            self.settings["color"] = "#FF0000"

    def initialize(self):
        self.make_priority()
        self.add_event("mycroft.internet.connected",
                       self.handle_internet_connected)
        self.start_internet_check()

    def make_priority(self):
        if not self.skill_id:
            # might not be set yet....
            return
        # load the current list of already blacklisted skills
        priority_list = self.config_core["skills"]["priority_skills"]

        # add the skill to the blacklist
        if self.skill_id not in priority_list:
            priority_list.insert(0, self.skill_id)

            # load the user config file (~/.mycroft/mycroft.conf)
            conf = LocalConf(USER_CONFIG)
            if "skills" not in conf:
                conf["skills"] = {}

            # update the blacklist field
            conf["skills"]["priority_skills"] = priority_list

            # save the user config file
            conf.store()

    # internet watchdog
    def start_internet_check(self):
        create_daemon(self._watchdog)

    def stop_internet_check(self):
        self.monitoring = False

    def _watchdog(self):
        self.monitoring = True
        output = subprocess.check_output("nmcli connection show | grep wifi",
                                         shell=True).decode("utf-8")
        if output.strip():
            self.log.info("Detected previously configured wifi, starting "
                          "grace period to allow it to connect")
            sleep(self.grace_period)
        while self.monitoring:
            if self.in_setup:
                sleep(1)  # let setup do it's thing
                continue

            if not connected():
                self.log.info("NO INTERNET")
                if not self.is_connected_to_wifi():
                    self.log.info("LAUNCH SETUP")
                    try:
                        self.launch_wifi_setup()  # blocking
                    except Exception as e:
                        self.log.exception(e)
                else:
                    self.log.warning("CONNECTED TO WIFI, BUT NO INTERNET!!")
            sleep(self.time_between_checks)

    # wifi setup
    @staticmethod
    def get_wifi_ssid():
        SSID = None
        try:
            SSID = subprocess.check_output(["iwgetid", "-r"]).strip()
        except subprocess.CalledProcessError:
            # If there is no connection subprocess throws a 'CalledProcessError'
            pass
        return SSID

    @staticmethod
    def is_connected_to_wifi():
        return WifiConnect.get_wifi_ssid() is not None

    def launch_wifi_setup(self):
        self.stop_setup()
        self.in_setup = True
        self.wifi_process = pexpect.spawn(
            self.wifi_command.format(ssid=self.ssid)
        )
        # https://github.com/pexpect/pexpect/issues/462
        self.wifi_process.delayafterclose = 1
        self.wifi_process.delayafterterminate = 1
        prev = ""
        restart = False
        if self.debug:
            self.speak_dialog("start_setup")
        while self.in_setup:
            try:
                out = self.wifi_process.readline().decode("utf-8").strip()
                if out == prev:
                    continue
                prev = out
                if out.startswith("Access points: "):
                    aps = list(out.split("Access points: ")[-1])
                    self.log.info(out)
                    if self.debug:
                        self.speak_dialog("wifi_scanned")
                elif out.startswith("Starting access point..."):
                    if self.debug:
                        self.speak_dialog("ap_start")
                elif out.startswith("Access point ") and \
                        out.endswith("created"):
                    self.prompt_to_join_ap()
                    if self.debug:
                        self.speak_dialog("ap_created")
                elif out.startswith("Starting HTTP server on"):
                    self.log.debug(out)
                    if self.debug:
                        self.speak_dialog("http_started")
                elif out.startswith("Stopping access point"):
                    if self.debug:
                        self.speak_dialog("ap_stop")
                elif out.startswith("Access point ") and \
                        out.endswith("stopped"):
                    if self.debug:
                        self.speak_dialog("ap_stopped")
                elif out == "User connected to the captive portal":
                    self.log.info(out)
                    self.prompt_to_select_network()
                    if self.debug:
                        self.speak_dialog("user_connected")
                elif out.startswith("Connecting to access point"):
                    if self.debug:
                        self.speak_dialog("connecting")
                elif out.startswith("Internet connectivity established"):
                    self.log.info(out)
                    self.report_setup_complete()
                    if self.debug:
                        self.speak_dialog("wifi_connected")
                elif "Error" in out or "[Errno" in out:
                    self.log.error(out)
                    self.report_setup_failed()

                    # TODO figure out at least the errors handled gracefully
                    accepted_errors = [
                        "Password length should be at least 8 characters"
                    ]
                    for e in accepted_errors:
                        if e in out:
                            continue
                    else:
                        restart = True
                        break

                if self.debug:
                    self.log.debug(out)
            except pexpect.exceptions.EOF:
                # exited
                self.log.info("Exited wifi setup process")
                break
            except pexpect.exceptions.TIMEOUT:
                # nothing happened for a while
                pass
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log.exception(e)
                break
        self.stop_setup()
        if restart:
            # handle bugs in balena, sometimes it fails to come back up
            # seems to happen on
            # Error: Getting access points failed
            self.launch_wifi_setup()
        elif self.debug:
            self.speak_dialog("end_setup")

    # intents
    @intent_handler("launch_setup.intent")
    def wifi_intent(self, message):
        self.launch_wifi_setup()

    # bus events
    def handle_internet_connected(self, message=None):
        """System came online later after booting."""
        self.enclosure.mouth_reset()
        self.stop_setup()  # just in case
        self.gui.release()

    # GUI events
    def prompt_to_join_ap(self, message=None):
        """Provide instructions for setting up wifi."""
        self.gui.remove_page("status.qml")
        self.gui["phone_image"] = "1_phone_connect-to-ap.png"
        self.gui["prompt"] = "Connect to the \nWifi network"
        self.gui["highlight"] = self.ssid
        self.gui["color"] = self.settings["color"]
        self.gui.show_page("prompt.qml")
        # allow GUI to linger around for a bit, will block the wifi setup loop
        sleep(2)

    def prompt_to_select_network(self, message=None):
        """Prompt user to select network and login."""
        self.gui.remove_page("status.qml")
        self.gui.clear()
        self.gui["phone_image"] = "3_phone_choose-wifi.png"
        self.gui["prompt"] = "Choose the \nWifi network to \nconnect your \ndevice"
        self.gui["highlight"] = ""
        self.gui["color"] = self.settings["color"]
        self.gui.show_page("prompt.qml")
        # allow GUI to linger around for a bit, will block the wifi setup loop
        sleep(2)

    def report_setup_complete(self, message=None):
        """Wifi setup complete, network is connected."""
        self.gui.remove_page("prompt.qml")
        self.gui.clear()
        self.gui["icon"] = "check-circle.svg"
        self.gui["label"] = "Connected"
        self.gui["bgColor"] = "#40DBB0"
        self.gui.remove_page("prompt.qml")
        self.gui.show_page("status.qml")
        # allow GUI to linger around for a bit, will block the wifi setup loop
        sleep(3)
        self.gui.release()

    def report_setup_failed(self, message=None):
        """Wifi setup failed"""
        self.speak_dialog("wifi_error")
        self.gui.remove_page("prompt.qml")
        self.gui.clear()
        self.gui["icon"] = "times-circle.svg"
        self.gui["label"] = "Connection Failed"
        self.gui["bgColor"] = "#FF0000"
        self.gui.show_page("status.qml")
        # allow GUI to linger around for a bit, will block the wifi setup loop
        sleep(2)

    # cleanup
    def stop_setup(self):
        if self.wifi_process is not None:
            try:
                if self.wifi_process.isalive():
                    self.log.debug("terminating wifi setup process")
                    self.wifi_process.sendcontrol('c')
                    sleep(1)
                    self.wifi_process.close()
                    sleep(1)
                if self.wifi_process.isalive():
                    self.log.warning('wifi setup did not exit gracefully.')
                    self.wifi_process.close(force=True)
                    sleep(1)
                    if self.wifi_process.isalive():
                        self.log.warning('trying to terminate wifi setup process')
                        self.wifi_process.terminate()
                        sleep(1)
                else:
                    self.log.debug('wifi setup exited gracefully.')
            except Exception as e:
                self.log.exception(e)
        self.wifi_process = None
        self.in_setup = False

    def shutdown(self):
        self.monitoring = False
        self.stop_setup()


def create_skill():
    return WifiConnect()


