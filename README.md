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
