# <img src='https://camo.githubusercontent.com/48b782bbddb51b97cf2971fda5817080075f7799/68747470733a2f2f7261772e6769746861636b2e636f6d2f466f7274417765736f6d652f466f6e742d417765736f6d652f6d61737465722f737667732f736f6c69642f636f67732e737667' width='50' height='50' style='vertical-align:bottom'/> OpenVoiceOS - Mycroft Edition
A minimalistic Linux OS bringing the open source voice assistant Mycroft A.I. to embbeded, low-spec headless and/or small (touch)screen devices.

## System.
### OpenVoiceOS - Full 64 Bit distribution
- Linux kernel 5.10.x (LTS)
- Buildroot 2021.02.x (LTS)
- Mycroft 20.08.x (mycroft-lib pip installable version)
- Raspberry Pi 3|3b|3b+ (Initial development hardware = 3b)
- Raspberry Pi 4 (Current development hardware)

## Stats:

| [![Build Status](https://travis-ci.org/OpenVoiceOS/OpenVoiceOS.svg?branch=master)](https://travis-ci.org/OpenVoiceOS/OpenVoiceOS) | [![GitHub last commit](https://img.shields.io/github/last-commit/google/skia.svg)](https://github.com/OpenVoiceOS/OpenVoiceOS/commits/develop) |
|:---:|:---:|
| This shows if the code is valid and can be build. | This shows when this repo was updated for the last time |
| [![GitHub stars](https://img.shields.io/github/stars/OpenVoiceOS/OpenVoiceOS.svg)](https://github.com/OpenVoiceOS/OpenVoiceOS/stargazers) | [![GitHub issues](https://img.shields.io/github/issues/OpenVoiceOS/OpenVoiceOS.svg)](https://github.com/OpenVoiceOS/OpenVoiceOS/issues) |
| Please :star: this repo if you find it useful | Issues are like my personal TODO list and information archive |
|[![License: Apache License 2.0](https://img.shields.io/crates/l/rustc-serialize.svg)](http://www.apache.org/licenses/LICENSE-2.0.html)| [![contributions welcome](https://img.shields.io/badge/contributions-welcome-blue.svg?style=flat)](https://github.com/OpenVoiceOS/OpenVoiceOS/pulls) |
| I'm using the Apache License 2.0 similar as Mycroft A.I. which means commercial use is allowed | If you have any ideas, they're always welcome.  Either submit an issue or a PR! |
| [![Uptime Robot status](https://img.shields.io/website-up-down-green-red/https/shields.io.svg?label=j1nx.nl)](https://stats.uptimerobot.com/Y5L6rSB07) | [![Buy me a](https://img.shields.io/badge/BuyMeABeer-Paypal-blue.svg)](https://www.paypal.me/j1nxnl) |
| I use uptime robot to monitor for things i can't monitor when the connection drops. | If you feel the need, now it's as easy as clicking this button! |

## Getting started.
At this moment development is in very early stages and focussed on the Raspberry Pi 3B & 4. As soon as an initial first workable version
is created, other hardware might be added.

### Getting the code.
First, get the code on your system! The simplest method is via git.
<br>
- cd ~/
- git clone --recurse-submodules https://github.com/OpenVoiceOS/OpenVoiceOS.git
- cd OpenVoiceOS

### Patching Buildroot.
*(ONLY at the first clean checkout/clone)* If this is the very first time you are going to build an image, you need to execute the following command once;
<br>
- ./scripts/br-patches.sh
<br>
This will patch the Buildroot packages.

## Building the image.
Building the image(s) can be done by utilizing a proper Makefile;
<br>
To see the available commands, just run: 'make help'
<br>
As example to build the rpi3 version;<br>
- make clean
- make rpi4_64-gui-config
- make rpi4_64-gui

Now grab a cup of coffee, go for a walk, sleep and repeat as the build process takes up a long time pulling everything from source and cross compiling everything for the device. Especially the qtwebengine package is taking a LONG time.
<br>
(At the moment there is an outstanding issue which prevents the build to run completely to the end. The plasma-workspace package will error out, not finding the libGLESv4 properly linked within QT5GUI. When the build stopped bacause of this error, edit the following file;
<br>
buildroot/output/host/aarch64-buildroot-linux-gnu/sysroot/usr/lib/cmake/Qt5Gui/Qt5GuiConfigExtras.cmake
<br>
at the bottom of the file replace this line;
<br>
_qt5gui_find_extra_libs(OPENGL "GLES" "" "")
<br>And replace it bit this line;<br>
_qt5gui_find_extra_libs(OPENGL "${CMAKE_SYSROOT}/usr/lib/libGLESv2.so" "" "${CMAKE_SYSROOT}/usr/include/libdrm")
<br>
Then you can continue the build process by re-running the "make rpi4_64-gui" command. (DO NOT, run "make clean" and/or "make rpi4_64-gui-config" again, or you will start from scratch again !!!)
<br>
When everything goes fine the xz compressed image will be available within the release directory.

## Documentation.
More information and instructions can be found within the "documentation" folder.

## Credits
Mycroft AI (@MycroftAI)<br>
Buildroot (@buildroot)
HelloChatterbox (@hellochatterbox)

### Inspired by;
HassOS (@home-assistant)<br>
