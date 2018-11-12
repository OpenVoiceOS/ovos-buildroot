# <img src='https://rawgithub.com/FortAwesome/Font-Awesome/master/advanced-options/raw-svg/solid/cogs.svg' card_color='#22a7f0' width='50' height='50' style='vertical-align:bottom'/> MycroftOS
MycroftOS is a bare minimal linux OS based on Buildroot to run the Mycroft A.I. software stack on embedded devices. 
The software stack of Mycroft creates a hackable open source voice assistant.

More information about the development, process, ideas etc. at https://www.j1nx.nl
More information about the Mycroft A.I. software stack at https://mycroft.ai

## System.
- Linux kernel 4.14 (LT)
- Buildroot 2018.08.x
- Mycroft 18.08.x
- Raspberry Pi 3B (initial development hardware)

## Stats:

| [![Build Status](https://travis-ci.org/j1nx/MycroftOS.svg?branch=develop)](https://travis-ci.org/j1nx/MycroftOS) || [![GitHub last commit](https://img.shields.io/github/last-commit/google/skia.svg)](https://github.com/j1nx/MycroftOS/commits/develop) |
|:---:|:---:|
| This shows if the code is valid and can be build. | This shows when this repo was updated for the last time |
| [![GitHub stars](https://img.shields.io/github/stars/j1nx/MycroftOS.svg)](https://github.com/j1nx/MycroftOS/stargazers) | [![GitHub issues](https://img.shields.io/github/issues/j1nx/home_assistant_config.svg)](https://github.com/j1nx/MycroftOS/issues) |
| Please :star: this repo if you find it useful | Issues are like my personal TODO list and information archive |
|[![License: Apache License 2.0](https://img.shields.io/crates/l/rustc-serialize.svg)](http://www.apache.org/licenses/LICENSE-2.0.html)| [![contributions welcome](https://img.shields.io/badge/contributions-welcome-blue.svg?style=flat)](https://github.com/j1nx/MycroftOS/pulls) |
| I'm using the Apache License 2.0 similar as Mycroft A.I. which means commercial use is allowed | If you have any ideas, they're always welcome.  Either submit an issue or a PR! |
| [![Uptime Robot status](https://img.shields.io/website-up-down-green-red/https/shields.io.svg?label=j1nx.nl)](https://stats.uptimerobot.com/Y5L6rSB07) | [![Buy me a](https://img.shields.io/badge/BuyMeABeer-Paypal-blue.svg)](https://www.paypal.me/j1nxnl) |
| I use uptime robot to monitor for things i can't monitor when the connection drops. | If you feel the need, now it's as easy as clicking this button! |

## Getting started.
At this moment development is in very early stages and focussed on the Raspberry Pi 3B. As soon as an initial first workable version
is created, other hardware might be added.

### Getting the code.
First, get the code on your system! The simplest method is via git.

- cd ~/
- git clone --recurse-submodules https://github.com/j1nx/MycroftOS.git
- cd MycroftOS

If this is the very first time you are going to build an image, you need to execute the following command once;
- ./scripts/br-patches.sh

### Building the code.
Then we can build the image(s) by running the following command;
- ./scripts/build.sh
(At this moment only one image get's build. Namely the one for RPi3B. Later on in time this section will get expanded with other hardware such as, the other Raspberry Pi's, perhaps Mark-1 and/or Mark-2 and further down the road for the new Rockchip RK3399Pro SoC with RK1808 NPU

... More building instructions will follow soon ...

## Credits
Mycroft AI (@MycroftAI)
Buildroot (@buildroot)

Inspired by;
HassOS (@home-assistant)
Recalbox (Gitlab - @recalbox)
