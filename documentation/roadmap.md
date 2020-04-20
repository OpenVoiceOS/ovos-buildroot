---------------------------------------
**MycroftOS - Version 0.1.0 - alpha 8**

ChangeLog:

- ~~Ondemand governor for both RPI3 and 4 (instead of performance)~~ [DONE]
- ~~Fix: MPV not compiling because of missing LD stuff~~ [DONE]
- ~~Update to latest LTS kernel and drivers / firmwares~~ [DONE]
- ~~Update to latest LTS buildroot (20.02.1)~~ [DONE]
- ~~Update to latest Mycroft version and dependencies~~ [DONE]
- ~~Addition of additional packages for the near future~~ [DONE]
  * ~~OpenCV~~ [DONE]
  * ~~espeak~~ [DONE]
  * ~~Python-Numpy~~ [DONE]
  * ~~Motion~~ [DONE]
  * ~~Mosquitto~~ [DONE]
  * ~~Squeezelite~~ [DONE]
- ~~Add the last bits of the LAN-MAC address to the hostname~~ [DONE]
- ~~Update spotifyd to latest 0.2.24 version~~ [DONE]
- ~~Update snapcast to latest 0.19.0 version~~ [DONE]
- ~~Update respeaker driver to latest dev version.~~ [DONE]
- ~~More microphone support~~ [DONE]
  * ~~PS3 Eye~~ [DONE]
- ~~Cleanup buildroot:~~ [DONE]
  * ~~rootfs default overlay seperate~~ [DONE]
  * ~~device specific overlays~~ [DONE]
- ~~Look into animating the boot splash screen, showing progress during boot~~ [DONE]
  * ~~Add and implement psplash~~ [DONE]
  * ~~Update all services to update psplash~~ [DONE]
- ~~Change the wording on the splash screens;~~ [DONE (Removed)]
  * ~~Safe to reboot -> Safe to reboot / Rebootig now~~ [DONE (Removed)]
  * ~~Safe to poweroff -> Safe to poweroff / Powering off~~ [DONE (Removed)]
- ~~Make use of systemd preset files (/usr/lib/systemd/system-preset/<prio>-<name>.preset)~~ [DONE]
  * ~~wpa_supplicant@wlan0.service~~ [DONE]
  * ~~wpa_supplicant@ap0.service~~ [DONE]
  * ~~Enable any other mycroftos services that needs to be enabled by default~~ [DONE]
  * ~~Remove all systemd (enabled) symlinks in the external packages~~ [DONE]
  * ~~Disable any newly installed service by default. (/usr/lib/systemd/system-preset/99-default.preset)~~ [DONE]
  * ~~wpa_supplicant systemd file can now be placed in rootfs-overlay / patch to be removed~~ [DONE]
- ~~Fix python-speechrecognition package. Do not copy flac binaries~~ [DONE]


TODO:

WiFi:
- WiFi does not come to life after setup with new 2020.02.1 version (found cause: see systemd preset task above)
- Add 5G support to the wifi system (Country setting most likely)

Enclosure:  
- Implement initial framebuffer drawing GUI
  * Look into showing the pairing code on the HDMI as well (look at mycroft's system)
  * Look into showing the IP address on the HDMI as well (look at mycroft's system)
  * Look into combining the wifi code, the framebuffer code and the enclosure code into one system.
- Move over / Integrated the WiFi setup into the Enclosure code.
  * Change WifiSetup splash; MycroftOS-Setup -> MycroftOS-WiFiSetup
  * Have a look at the wifi scan to exclude non real SSID (“ID List”)
  * Figure out how to make the wifi password box to be able to show password (eye icon)
- Enclosure code for enabling services, halt, reboot, etc
- Enclosure code for pulseaudio control (volume mostly)

System:
- Systemd notify and Watchdog support to make starting/stopping/restarting and failures way more robust. [WIP]
- Enable (hardware) watchdog support.
- Include changing the hostname from the MycroftOS settings skill without messing up above MAC addition.
- Look into the msm error/warning "no package manager found" (there is none, but just handle the warning)
- Included volume skill can't be updated
  * Should be changed to pulseaudio anyway, but...
  * Check if the included volume-skill can be updated, via offical git commits
- Avahi zero config publish to be set up (pulseaudio, mpd, snapcast, etc.)
- MycroftOS settings skill to be able to setup smart speaker services / software
- VLC Framebuffer video playing support (if not accelerated, check omxplayer but needs to be created as audio backend within mycroft)
- Add and make configurable, where sound output has to go;
  * BT Speaker (A2DP) normal (Use a bluetooth speaker as output)
  * Bluetooth mic/speaker combo support using HSP (use headsets as input/output for Mycroft)
  * Airplay (example: SONOS) using module-raop-discover and module-raop-sink of PulseAudio
  * Autoconnect trusted BT devices as soon as it sees them using: module-switch-on-connect from PulseAudio

Documentation:
- Change README with all new changes [WIP]
- Update / Complete "documentation" folder and docs
  * Building.md
  * Boards.md
  * Kernel.md
  * Python-packages.md
- Instructions / Wiki for most common and different aspects and functions;
  * Installation
  * First run
  * Configuration
    - Smart speaker functions
	- System Services
  * Spotify setup
  * Squeezelite setup
  * Snapcast Client/Server setup
  * Bluetooth speaker output setup
  * Airplay speaker output setup

Cleanup & Maintenance:
- Fix / Check all Buildroot package dependencies (SELECT and DEPENDS references within Config.in)
- Cleanup buildroot config file
  * remove / disable any unused packages that might have slipped in while testing / debugging / etc.
- Make sure all Skills from the market can install (python dependencies either available or pre-installed)


---------------------------------------
**MycroftOS - Version 1.0.0**

TODO:

- Add an first initial GUI system just as Mycroft.ai (QT5)

- Cleanup the kernel config
  * Remove unused drivers and stuff (DVB and such)
  * Separate default config into systeemwide .config
  * Board specific configs as overlays

- Implement easy (OTA) update system (RAUC or SWUpdate, not sure yet)

- Support for more devices / boards
  * OVA (Virtual system - Virtualbox)


---------------------------------------
**MycroftOS - Version 1.1.0**

- Build precise from source at build time (0.3.0 dev version)
  * create buildroot packages for all dependencies.
  * create buildroot package for precise-engine & runner
  * create buildroot package for wake word modules (including the commodity ones)
  * figure out how to give back to the communicty by allowing recording of wake words easily

- Support for more devices / boards
  * Rockchip boards
  * ReSpeaker Pro V2
  * Odroid
  * X86 / 64
  * etc. / ideas

- Implement first initial WEB frontend/backend system for configuration and all
  * Backend for settings, configuration and update
  * Backend pulseaudio control (Already available project as quick fix, but needs to integrate with MycroftOS system)
  * Frontend for possibly accelerated browser hooking into the Mycroft GUI

- 64bit support for RPI3 ~~and RPI4~~ [WIP]

- More hardware/microphone support
  * Google-AIY
  * Kinect-360

- ReSpeaker Mycroft LED pattern which is blue-isch and looks like the logo of Mycroft

