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
We can build the image(s) by running the following command;
<br>
- ./scripts/build.sh
<br>
At this moment only one image get's build. Namely the one for RPi3. Later on in time this section will get expanded with other possible supported hardware.

