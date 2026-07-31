# <img src='https://camo.githubusercontent.com/48b782bbddb51b97cf2971fda5817080075f7799/68747470733a2f2f7261772e6769746861636b2e636f6d2f466f7274417765736f6d652f466f6e742d417765736f6d652f6d61737465722f737667732f736f6c69642f636f67732e737667' width='50' height='50' style='vertical-align:bottom'/> OVOS - Buildroot OS

This is a minimal Linux OS for [ovos-core](https://github.com/OpenVoiceOS/ovos-core), the open source voice assistant. It runs on embedded devices, low-spec headless devices, and small touchscreen devices.

## System

The OpenVoiceOS full 64-bit distribution has these parts:

- Linux kernel 6.1.x (LTS)
- Buildroot 2023.02.x (LTS), with local modifications
- The OVOS framework, packaged through ovos-docker containers (currently the latest alpha/development version)
- Support for Raspberry Pi 3, 3b, and 3b+ (UEFI based)
- Support for Raspberry Pi 4 (UEFI based)
- Support for x86_64 Intel based computers (UEFI based, work in progress)
- Support for Open Virtual Appliance (UEFI based)

## Stats

| [![Build Status](https://travis-ci.org/OpenVoiceOS/OpenVoiceOS.svg?branch=master)](https://travis-ci.org/OpenVoiceOS/OpenVoiceOS) | [![GitHub last commit](https://img.shields.io/github/last-commit/google/skia.svg)](https://github.com/OpenVoiceOS/OpenVoiceOS/commits/develop) |
|:---:|:---:|
| This badge shows if the code builds. | This badge shows the date of the last update to this repo. |
| [![GitHub stars](https://img.shields.io/github/stars/OpenVoiceOS/OpenVoiceOS.svg)](https://github.com/OpenVoiceOS/OpenVoiceOS/stargazers) | [![GitHub issues](https://img.shields.io/github/issues/OpenVoiceOS/OpenVoiceOS.svg)](https://github.com/OpenVoiceOS/OpenVoiceOS/issues) |
| Star this repo if you find it useful. | Issues track planned work and notes. |
|[![License: Apache License 2.0](https://img.shields.io/crates/l/rustc-serialize.svg)](http://www.apache.org/licenses/LICENSE-2.0.html)| [![contributions welcome](https://img.shields.io/badge/contributions-welcome-blue.svg?style=flat)](https://github.com/OpenVoiceOS/OpenVoiceOS/pulls) |
| This project uses the Apache License 2.0, the same license as Mycroft AI. It allows commercial use. | Contributions are welcome. Submit an issue or a pull request. |
| [![Uptime Robot status](https://img.shields.io/website-up-down-green-red/https/shields.io.svg?label=j1nx.nl)](https://stats.uptimerobot.com/Y5L6rSB07) | [![Buy me a](https://img.shields.io/badge/BuyMeABeer-Paypal-blue.svg)](https://www.paypal.me/j1nxnl) |
| Uptime Robot monitors the site for outages that other tools do not catch. | Use this button to support the project. |

## Documentation

See the [`documentation`](documentation/README.md) folder for setup and build instructions.

## Credits

Mycroft AI ([@MycroftAI](https://github.com/MycroftAI))<br>
Buildroot ([@buildroot](https://github.com/buildroot))<br>
HassOS ([@home-assistant](https://github.com/home-assistant))<br>

### Inspired by

HassOS ([@home-assistant](https://github.com/home-assistant))<br>
SkiffOS ([@skiffos](https://github.com/skiffos))
