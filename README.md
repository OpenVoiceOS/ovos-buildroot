# <img src='https://camo.githubusercontent.com/48b782bbddb51b97cf2971fda5817080075f7799/68747470733a2f2f7261772e6769746861636b2e636f6d2f466f7274417765736f6d652f466f6e742d417765736f6d652f6d61737465722f737667732f736f6c69642f636f67732e737667' width='50' height='50' style='vertical-align:bottom'/> Open Voice Operating System - Buildroot Edition
A minimalistic Linux OS bringing the open source voice assistant [ovos-core](https://github.com/OpenVoiceOS/ovos-core) to embedded, low-spec headless and/or small (touch)screen devices.

## Table of Contents
1. [System](https://github.com/OpenVoiceOS/ovos-buildroot#system)
2. [Stats](https://github.com/OpenVoiceOS/ovos-buildroot#stats)
3. [Getting Started](https://github.com/OpenVoiceOS/ovos-buildroot#getting-started)
4. [Building Guide](https://github.com/OpenVoiceOS/ovos-buildroot#building)
5. [Documentation](https://github.com/OpenVoiceOS/ovos-buildroot#documentation)
6. [Credits](https://github.com/OpenVoiceOS/ovos-buildroot#credits)

## System
### OpenVoiceOS - Full 64 Bit distribution
- Linux kernel 6.1.x (LTS)
- Buildroot 2023.02.x (LTS) (With some modification here and there)
- OVOS framework / software package utilizing ovos-docker containers (Currently latest alpha/development version)
- Raspberry Pi 3|3b|3b+
- Raspberry Pi 4 
- x86_64 Intel based computers (UEFI based)
- Open Virtual Appliance (UEFI based)

## Stats

| [![Build Status](https://travis-ci.org/OpenVoiceOS/OpenVoiceOS.svg?branch=master)](https://travis-ci.org/OpenVoiceOS/OpenVoiceOS) | [![GitHub last commit](https://img.shields.io/github/last-commit/google/skia.svg)](https://github.com/OpenVoiceOS/OpenVoiceOS/commits/develop) |
|:---:|:---:|
| This shows if the code is valid and can be build. | This shows when this repo was updated for the last time |
| [![GitHub stars](https://img.shields.io/github/stars/OpenVoiceOS/OpenVoiceOS.svg)](https://github.com/OpenVoiceOS/OpenVoiceOS/stargazers) | [![GitHub issues](https://img.shields.io/github/issues/OpenVoiceOS/OpenVoiceOS.svg)](https://github.com/OpenVoiceOS/OpenVoiceOS/issues) |
| Please :star: this repo if you find it useful | Issues are like my personal TODO list and information archive |
|[![License: Apache License 2.0](https://img.shields.io/crates/l/rustc-serialize.svg)](http://www.apache.org/licenses/LICENSE-2.0.html)| [![contributions welcome](https://img.shields.io/badge/contributions-welcome-blue.svg?style=flat)](https://github.com/OpenVoiceOS/OpenVoiceOS/pulls) |
| I'm using the Apache License 2.0 similar as Mycroft A.I. which means commercial use is allowed | If you have any ideas, they're always welcome.  Either submit an issue or a PR! |
| [![Uptime Robot status](https://img.shields.io/website-up-down-green-red/https/shields.io.svg?label=j1nx.nl)](https://stats.uptimerobot.com/Y5L6rSB07) | [![Buy me a](https://img.shields.io/badge/BuyMeABeer-Paypal-blue.svg)](https://www.paypal.me/j1nxnl) |
| I use uptime robot to monitor for things i can't monitor when the connection drops. | If you feel the need, now it's as easy as clicking this button! |

  
## Getting Started
Only use x86_64 based architecture/ hardware to build the image. 

The following example Build environment has been tested :

- Architecture: x86_64 
- Hardware: Intel Core i5 processor, 8GB RAM, 240GB SSD (you can build on less RAM (2GB) and slower storage but more RAM, faster storage =  quicker image building)
- OS: Ubuntu 22.04 LTS desktop

#### Installing System Build Dependencies
Buildroot dependencies must be installed as a prerequisite. Below is a list of required dependencies.
- bash 
- bc 
- binutils 
- build-essential 
- bzip2 
- cpio 
- diffutils 
- file 
- findutils 
- gzip 
- libarchive-tools 
- make 
- patch 
- perl 
- rsync 
- sed 
- tar 
- unzip 
- wget 
- which

Assuming apt, the following command will install all of these required dependencies:

```
sudo apt-get install -y bash bc binutils build-essential bzip2 cpio diffutils file findutils gzip libarchive-tools make patch perl rsync sed tar unzip wget which
```
#### The following firewall ports need to be allowed to the internet.
In addition to the usual http/https ports (tcp 80, tcp 443) a couple of other ports need to be allowed to the internet :
- tcp 9418 (git).
- tcp 21 (ftp PASV) and random ports for DATA channel. 
  - This can be optional but better to have this allowed along with the corresponding random data channel ports. (knowledge of firewalls required)


### Installation

The simplest method is to download the source code is via git.
```
cd ~/
```
```
git clone --recurse-submodules https://github.com/OpenVoiceOS/OpenVoiceOS.git
```
```
cd OpenVoiceOS
```


## Building
Building the image(s) can be done by utilizing a proper Makefile. To see the available commands, just run: 

```
make help
```

As example to build the rpi4 version, run the following make commands: <br>
```
make clean
```
```
make rpi4_64
```

When everything goes fine, the created images/files will be available within the release directory.

## Documentation
More information and instructions can be found within the [Documentation](https://github.com/OpenVoiceOS/ovos-buildroot/tree/develop/documentation) folder.

## Credits
Mycroft AI (@MycroftAI)<br>
Buildroot (@buildroot)
HelloChatterbox (@hellochatterbox)<br>
HassOS (@home-assistant)<br>

### Inspired by:
HassOS (@home-assistant)<br>
