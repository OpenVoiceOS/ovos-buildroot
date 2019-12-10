# Building of MycroftOS from sources.

Flashable images will be provided at mayor, minor and hotfix release tags. However if you want to build the images from source yourself, below instructions will get you on your way.

## Getting the code.
First, get the code on your system! The simplest method is via git.
<br>
- cd ~/ 
- git clone --recurse-submodules https://github.com/j1nx/MycroftOS.git 
- cd MycroftOS 

## Patching Buildroot.
If this is the very first time you are going to build an image, you need to execute the following command once;
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
make clean<br>
make rpi3-config<br>
make rpi3<br>
<br>
To build all available buids, run;<br>
make all

